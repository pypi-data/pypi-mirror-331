import os
import requests
import pendulum
import getpass

from logging import getLogger
from pathlib import Path
from posixpath import join as urljoin
from configparser import ConfigParser
from typing import Optional, Tuple

logger = getLogger("sumatra.config")

_CONFIG_PATH = os.path.expanduser(
    os.environ.get("SUMATRA_CONFIG_PATH", os.path.join(Path.home(), ".sumatra"))
)
_CONFIG_FILE = os.path.join(_CONFIG_PATH, "config")


def _sanitize_instance(instance: str) -> Tuple[str, str]:
    if not instance:
        raise RuntimeError("Either provide 'instance' or run `sumatra login`")

    for localhost in ("localhost:", "127.0.0.1:", "0.0.0.0:"):
        if instance.startswith(localhost):
            return "http", instance.split("/")[0]
        if instance.startswith(f"http://{localhost}"):
            return "http", instance[7:].split("/")[0]

    if instance.startswith("http://"):
        raise ValueError("Sumatra Instance URL must start with https://")

    if instance.startswith("https://"):
        return "https", instance[8:].split("/")[0]

    return "https", instance.split("/")[0]


def _strip_suffix(url: str, suffix: str) -> str:
    if url and url.endswith(suffix):
        return url[: -len(suffix)]
    return url


class Config:
    def __init__(self, fname: str = _CONFIG_FILE):
        self._fname = fname
        self._config = ConfigParser()
        self._config.read(fname)

        self._instance: Optional[str] = None
        self._instance_protocol: Optional[str] = None

    def _get(self, key: str) -> Optional[str]:
        env_key = "SUMATRA_" + key.upper()
        if env_key in os.environ:
            val = os.environ[env_key]
            logger.debug(f"Using ENV['{env_key}'] as {key}: '{val}'")
            return os.environ[env_key]
        if self.instance not in self._config:
            self._config.add_section(self.instance)
        try:
            val = self._config[self.instance][key]
            logger.debug(f"Using '{key}' from config file: '{val}'")
            return val
        except KeyError:
            logger.debug(f"Config variable '{key}' not found.")
            return None

    def _get_or_stack(self, key: str) -> str:
        val = self._get(key)
        if val is None:
            self.update_from_stack()
            val = self._get(key)
        if val is None:
            raise KeyError
        return val

    def _set(self, key: str, val: str) -> str:
        if self.instance not in self._config:
            self._config.add_section(self.instance)
        self._config[self.instance][key] = val
        return val

    def _fetch_stack(self) -> dict[str, str]:
        stack_config_url = urljoin(self.instance_url, "stack.json")
        logger.info(f"Fetching stack config from {stack_config_url}")
        response = requests.get(stack_config_url)
        response.raise_for_status()
        try:
            resp_json: dict[str, str] = response.json()
            return resp_json
        except:
            raise Exception("error fetching stack config from: " + stack_config_url)

    def summary(self, unmask=False):
        return f"""Config File: {_CONFIG_FILE}
Tokens File: {self.jwt_tokens_path}

instance:       {self.instance}
workspace:      {self.workspace}
default_branch: {self.default_branch}
scowl_dir:      {self.scowl_dir}
timezone:       {self.timezone}

api_event_url:       {self.api_event_url}
console_graphql_url: {self.console_graphql_url}
sdk_graphql_url:     {self.sdk_graphql_url}

api_key: {"<masked>" if self.api_key and not unmask else self.api_key}
sdk_key: {"<masked>" if self.sdk_key and not unmask else self.sdk_key}
"""

    def update_from_stack(self, stack: Optional[dict[str, str]] = None) -> None:
        stack = stack or self._fetch_stack()
        self._set("user_pool_client_id", stack["user_pool_client_id"])
        self._set("user_pool_id", stack["user_pool_id"])
        user_pool_domain = stack["user_pool_domain"]
        self._set(
            "cognito_auth_url",
            f"https://{user_pool_domain}.auth.us-east-1.amazoncognito.com/login",
        )
        self._set(
            "cognito_token_url",
            f"https://{user_pool_domain}.auth.us-east-1.amazoncognito.com/oauth2/token",
        )
        self._set("console_endpoint", stack["console_uri"])
        api_uri = stack["api_uri"]
        self._set("api_endpoint", api_uri)
        self._set("server_version", stack.get("version", "v1.2.0"))
        sdk_uri = stack["sdk_uri"]
        sdk_vpce_ids = stack["sdk_vpc_endpoint_ids"]
        if sdk_vpce_ids:
            sdk_uri = sdk_uri.replace(".execute-api", f"-{sdk_vpce_ids[0]}.execute-api")
        self._set("sdk_endpoint", sdk_uri)
        self._set("aws_region", stack["aws_region"])
        self.save(update_default_instance=False)

    @property
    def instance(self) -> str:
        if not self._instance:
            self.instance = os.environ.get("SUMATRA_INSTANCE") or self._config[
                "DEFAULT"
            ].get("instance")
        if not self._instance:
            raise RuntimeError("Either provide 'instance' or run `sumatra login`")
        return self._instance

    @instance.setter
    def instance(self, instance: str) -> None:
        self._instance_protocol, self._instance = _sanitize_instance(instance)

    @property
    def instance_url(self) -> str:
        instance = self.instance
        return f"{self._instance_protocol}://{instance}"

    @property
    def api_key(self) -> Optional[str]:
        return self._get("api_key")

    @property
    def sdk_key(self) -> Optional[str]:
        return self._get("sdk_key")

    @property
    def jwt_token(self) -> Optional[str]:
        return self._get("jwt_token")

    @property
    def jwt_tokens_path(self) -> str:
        return self._get("jwt_tokens_path") or os.path.join(_CONFIG_PATH, ".jwt-tokens")

    @property
    def default_branch(self) -> str:
        return self._get("default_branch") or "dev_" + getpass.getuser()

    @default_branch.setter
    def default_branch(self, branch: str) -> None:
        self._set("default_branch", branch)
        self.save(update_default_instance=False)

    @property
    def workspace(self) -> str:
        return self._get("workspace")

    @workspace.setter
    def workspace(self, workspace: str) -> None:
        self._set("workspace", workspace)
        self.save(update_default_instance=False)

    @property
    def timezone(self) -> Optional[str]:
        return self._get("timezone") or pendulum.now().timezone_name

    @property
    def scowl_dir(self) -> str:
        return self._get("scowl_dir") or "."

    @property
    def server_version(self) -> str:
        return self._get_or_stack("server_version")

    @property
    def user_pool_id(self) -> str:
        return self._get_or_stack("user_pool_id")

    @property
    def user_pool_domain(self) -> str:
        return self._get_or_stack("user_pool_domain")

    @property
    def user_pool_client_id(self) -> str:
        return self._get_or_stack("user_pool_client_id")

    @property
    def cognito_auth_url(self) -> str:
        auth_url = self._get("cognito_auth_url")
        if auth_url:
            return auth_url
        return self._set(
            "cognito_auth_url",
            f"https://{self.user_pool_domain}.auth.us-east-1.amazoncognito.com/login",
        )

    @property
    def cognito_token_url(self) -> str:
        token_url = self._get("cognito_token_url")
        if token_url:
            return token_url
        return self._set(
            "cognito_token_url",
            f"https://{self.user_pool_domain}.auth.us-east-1.amazoncognito.com/oauth2/token",
        )

    @property
    def api_endpoint(self) -> str:
        return _strip_suffix(self._get_or_stack("api_endpoint"), "/event")

    @property
    def api_event_url(self) -> str:
        return urljoin(self.api_endpoint, "event")

    @property
    def console_endpoint(self) -> str:
        return _strip_suffix(self._get_or_stack("console_endpoint"), "/graphql")

    @property
    def console_graphql_url(self) -> str:
        return urljoin(self.console_endpoint, "graphql")

    @property
    def sdk_endpoint(self) -> str:
        return _strip_suffix(self._get_or_stack("sdk_endpoint"), "/graphql")

    @property
    def sdk_graphql_url(self) -> str:
        return urljoin(self.sdk_endpoint, "graphql")

    @property
    def certs_url(self) -> str:
        return self._get("certs_url") or "https://resources.sumatra.ai/certs/"

    @property
    def lrd_certs_url(self) -> str:
        return urljoin(self.certs_url, "l0.lrd.sumatra.ai")

    @property
    def aws_region(self) -> str:
        return self._get_or_stack("aws_region")

    def save(self, update_default_instance: bool = True) -> None:
        logger.info(f"Saving config to '{self._fname}'")
        if update_default_instance:
            self._config["DEFAULT"]["instance"] = self.instance
        os.makedirs(os.path.dirname(self._fname), exist_ok=True)
        with open(self._fname, "w") as f:
            self._config.write(f)


CONFIG = Config()
