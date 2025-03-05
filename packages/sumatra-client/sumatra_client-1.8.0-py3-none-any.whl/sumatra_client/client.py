import os
import re
import time
import json
import logging
import boto3
import gzip
import pendulum
import python_graphql_client
import requests
import base64
from typing import Any, Optional, Union, Tuple
from requests.auth import AuthBase
from sumatra_client.util import humanize_status, splitext
from sumatra_client.auth import SDKKeyAuth, CognitoJwtAuth
from sumatra_client.config import CONFIG
from sumatra_client.workspace import WorkspaceClient
from sumatra_client.base import BaseClient
from sumatra_client.materialization import Materialization
from sumatra_client.model import ModelVersion
from sumatra_client.table import TableVersion
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger("sumatra.client")

TENANT_PREFIX = "sumatra_"
DEPS_FILE = "deps.scowl"
TABLE_NAME_REGEXP = re.compile("^[a-z][a-zA-Z0-9_]*$")


def _load_scowl_files(dir: str) -> dict[str, str]:
    scowls = {}
    for fname in os.listdir(dir):
        if fname.endswith(".scowl") and fname != DEPS_FILE:
            scowl = open(os.path.join(dir, fname)).read()
            scowls[fname] = scowl
    return scowls


class Client(BaseClient):
    """
    Client to connect to Sumatra GraphQL API

    __Humans:__ First, log in via the CLI: `sumatra login`

    __Bots:__ Set the `SUMATRA_INSTANCE` and `SUMATRA_SDK_KEY` environment variables
    """

    def __init__(
        self,
        instance: Optional[str] = None,
        branch: Optional[str] = None,
        workspace: Optional[str] = None,
    ):
        """
        Create connection object.

        Arguments:
            instance: Sumatra instance url, e.g. `yourco.sumatra.ai`. If unspecified, the your config default will be used.
            branch: Set default branch. If unspecified, your config default will be used.
            workspace: Sumatra workspace name to connect to.
        """
        if instance:
            CONFIG.instance = instance
        self._branch = branch or CONFIG.default_branch
        self._workspace_arg = workspace or CONFIG.workspace
        self._workspace = None
        self._workspace_id = None
        if CONFIG.sdk_key:
            logger.info("Connecting via SDK key")
            auth: AuthBase = SDKKeyAuth()
            endpoint = CONFIG.sdk_graphql_url
        else:
            auth = CognitoJwtAuth(self.workspace)
            endpoint = CONFIG.console_graphql_url
        super().__init__(
            client=python_graphql_client.GraphqlClient(auth=auth, endpoint=endpoint),
        )

    @property
    def instance(self) -> str:
        """
        Instance name from client config, e.g. `'yourco.sumatra.ai'`
        """
        return CONFIG.instance

    @property
    def workspace(self) -> Optional[str]:
        """
        User's current workspace slug, e.g. `my-workspace`
        """
        if not self._workspace:
            self._workspace, self._workspace_id = self._choose_workspace()
        return self._workspace

    @property
    def workspace_id(self) -> Optional[str]:
        """
        User's current workspace id, e.g. `01ee8330-edf4-07ae-ae19-3ab915f227c8`
        """
        if not self._workspace_id:
            self._workspace, self._workspace_id = self._choose_workspace()
        return self._workspace_id

    def _choose_workspace(self) -> Tuple[Optional[str], Optional[str]]:
        if CONFIG.sdk_key:
            sdk_key_workspace, tenant_id = self._get_workspace_from_sdk_key()
            if self._workspace_arg and sdk_key_workspace != self._workspace_arg:
                raise ValueError(
                    f"SDK Key's workspace: '{sdk_key_workspace}' does not match "
                    f"chosen workspace: '{self._workspace_arg}'."
                )
            return sdk_key_workspace, tenant_id
        workspaces = WorkspaceClient().get_workspaces()
        if self._workspace_arg:
            for ws in workspaces:
                if ws["slug"] == self._workspace_arg:
                    return ws["slug"], ws["id"]
            raise ValueError(
                f"Workspace '{self._workspace_arg}' not found. "
                f"Choose one of: {sorted(ws['slug'] for ws in workspaces)}."
            )
        if len(workspaces) == 1:
            ws = workspaces[0]
            return ws["slug"], ws["id"]
        if len(workspaces) > 1:
            raise RuntimeError(
                "Unable to determine workspace. "
                "Specify a workspace or run `sumatra workspace select`."
            )
        raise RuntimeError("No workspaces found. Run `sumatra workspace create` first.")

    def _get_workspace_from_sdk_key(self):
        logger.debug("Fetching workspace from SDK key")
        query = """
            query Workspace {
                workspace {
                    id
                    slug
                }
            }
        """

        ret = self._execute_graphql(query=query)

        d = ret["data"]["workspace"]
        return d["slug"], d["id"]

    @property
    def branch(self) -> str:
        """
        Default branch name
        """
        return self._branch

    @branch.setter
    def branch(self, branch: str) -> None:
        self._branch = branch

    @property
    def boto(self) -> boto3.Session:
        """
        Boto3 session object
        """
        query = """
            query TempCredentials {
                tenant { credentials }
            }
        """

        ret = self._execute_graphql(query=query)

        creds = ret["data"]["tenant"]["credentials"]

        return boto3.Session(
            aws_access_key_id=creds["AccessKeyID"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
            region_name=CONFIG.aws_region,
        )

    def get_settings(self) -> dict:
        """
        Return settings metadata about the current workspace.

        Returns:
            Workspace settings
        """
        logger.debug("Fetching workspace")
        query = """
            query Settings {
                currentTenant {
                    billingEmail
                    monthlyEvents
                    name
                    slug
                    usagePlan
                    icon
                }
            }
        """

        ret = self._execute_graphql(query=query)

        return ret["data"]["currentTenant"]

    def update_settings(
        self,
        slug: Optional[str] = None,
        nickname: Optional[str] = None,
        billing_email: Optional[str] = None,
        icon: Optional[bytes] = None,
    ) -> dict:
        """
        Update workspace settings metadata.

        Arguments:
            slug: Desired slug of the new workspace. Must consist only of letters, numbers, '-', and '_'. If this slug is taken, a random one will be generated instead, which may be changed later.
            nickname: A human readable name for the new workspace
            billing_email: Billing email address on the account
            icon: Binary encoding of a PNG image to use as the workspace icon. Max size 50kb

        Returns:
            A dict of the updated workspace settings
        """

        query = """
            mutation UpdateSettings($id: String!, $name: String, $slug: String, $icon: String, $billingEmail: String) {
                updateTenant(id: $id, name: $name, slug: $slug, icon: $icon, billingEmail: $billingEmail) {
                    id
                    slug
                    name
                    billingEmail
                }
            }
        """

        if icon:
            icon = "data:image/png;base64," + base64.b64encode(icon).decode()

        ret = self._execute_graphql(
            query=query,
            variables={
                "id": self.workspace_id,
                "slug": slug,
                "name": nickname,
                "billingEmail": billing_email,
                "icon": icon,
            },
        )

        return ret["data"]["updateTenant"]

    def user_email(self) -> str:
        """
        Return the email address of the connected user.

        Returns:
            Email address
        """
        logger.debug("Fetching user")
        query = """
        query CurrentUser {
            currentUser {
                email
            }
        }
        """

        ret = self._execute_graphql(query=query)

        return ret["data"]["currentUser"]["email"]

    def sdk_key(self) -> str:
        """
        Return the SDK key for the connected workspace

        Returns:
            SDK key
        """
        logger.debug("Fetching tenant sdk key")
        query = """
            query SDKKey {
                currentTenant {
                    accessKeys(type: "sdk") {
                        nodes {
                            key
                        }
                    }
                }
            }
        """

        ret = self._execute_graphql(query=query)

        return ret["data"]["currentTenant"]["accessKeys"]["nodes"][0]["key"]

    def api_key(self) -> str:
        """
        Return the API key for the connected workspace

        Returns:
            API key
        """
        logger.debug("Fetching tenant api key")
        query = """
            query APIKey {
                currentTenant {
                    accessKeys(type: "api") {
                        nodes {
                            key
                        }
                    }
                }
            }
        """

        ret = self._execute_graphql(query=query)

        return ret["data"]["currentTenant"]["accessKeys"]["nodes"][0]["key"]

    def query_athena(self, sql: str) -> "pd.DataFrame":
        """
        Execute a SQL query against the Athena backend and return the
        result as a dataframe.

        Arguments:
            sql: SQL query (e.g. "select * from event_log where event_type='login' limit 10")

        Returns:
            Result of query
        """
        try:
            import awswrangler as wr
        except ImportError:
            raise ImportError(
                "awswrangler is required for Pandas DataFrame support. "
                "Install with: pip install awswrangler"
            )

        return wr.athena.read_sql_query(
            boto3_session=self.boto,
            sql=sql,
            database=TENANT_PREFIX + self.workspace_id,
            workgroup=TENANT_PREFIX + self.workspace_id,
        )

    def get_branch(self, branch: Optional[str] = None) -> dict:
        """
        Return metadata about the branch.

        Arguments:
            branch: Specify a branch other than the client default.

        Returns:
            Branch metadata
        """
        branch = branch or self._branch
        logger.info(f"Getting branch {branch}")
        query = """
            query BranchScowl($id: String!) { 
              branch(id: $id) { id, hash, events, creator, lastUpdated, error } 
            }
        """

        ret = self._execute_graphql(
            query=query,
            variables={"id": branch},
            error_prefix=f"error getting branch '{branch}'",
        )

        d = ret["data"]["branch"]
        if not d:
            raise ValueError(f"branch '{branch}' not found")

        row = {
            "name": d["id"],
            "creator": d["creator"],
            "update_ts": d["lastUpdated"],
            "event_types": d["events"],
        }

        if "error" in d and d["error"]:
            row["error"] = d["error"]

        return row

    def clone_branch(self, dest: str, branch: Optional[str] = None) -> None:
        """
        Copy branch to another branch name.

        Arguments:
            dest: Name of branch to be created or overwritten.
            branch: Specify a source branch other than the client default.
        """
        branch = branch or self._branch
        logger.info(f"Cloning branch {branch} to {dest}")
        query = """
            mutation CloneBranch($id: String!, $sourceId: String!) {
                cloneBranch(id: $id, sourceId: $sourceId) { id, creator, lastUpdated, scowl }
              }
        """

        self._execute_graphql(query=query, variables={"id": dest, "sourceId": branch})

    def _put_branch_object(
        self, key: str, scowl: str, branch: Optional[str] = None
    ) -> None:
        branch = branch or self._branch
        logger.info(f"Putting branch object {key} to branch {branch}")
        query = """
              mutation PutBranchObject($branchId: String!, $key: String!, $scowl: String!) {
                putBranchObject(branchId: $branchId, key: $key, scowl: $scowl) { key }
              }
        """

        self._execute_graphql(
            query=query, variables={"branchId": branch, "key": key, "scowl": scowl}
        )

    def create_branch_from_scowl(self, scowl: str, branch: Optional[str] = None) -> str:
        """
        Create (or overwrite) branch with single file of scowl source code.

        Arguments:
            scowl: Scowl source code as string.
            branch: Specify a source branch other than the client default.

        Returns:
            Name of branch created
        """

        branch = branch or self._branch
        logger.info(f"Creating branch '{branch}' from scowl")
        try:
            self.delete_branch(branch)
        except RuntimeError:
            pass

        self._put_branch_object("main.scowl", scowl, branch)

        b = self.get_branch(branch)
        if "error" in b:
            raise RuntimeError(b["error"])

        return b["name"]

    def create_branch_from_dir(
        self,
        scowl_dir: Optional[str] = None,
        branch: Optional[str] = None,
        deps_file: Optional[str] = None,
    ) -> str:
        """
        Create (or overwrite) branch with local scowl files.

        Arguments:
            scowl_dir: Path to local .scowl files.
            branch: Specify a source branch other than the client default.
            deps_file: Path to deps file [default: <scowl_dir>/deps.scowl]

        Returns:
            Name of branch created
        """
        scowl_dir = scowl_dir or CONFIG.scowl_dir
        deps_file = deps_file or os.path.join(scowl_dir, DEPS_FILE)
        branch = branch or self._branch
        logger.info(f"Creating branch '{branch}' from dir '{scowl_dir}'")

        try:
            self.delete_branch(branch)
        except RuntimeError:
            pass

        scowls = _load_scowl_files(scowl_dir)
        if os.path.exists(deps_file):
            scowls[DEPS_FILE] = open(deps_file).read()
        if not scowls:
            raise RuntimeError(
                f"Unable to push local dir. '{scowl_dir}' has no .scowl files."
            )

        for key in scowls:
            self._put_branch_object(key, scowls[key], branch)

        b = self.get_branch(branch)
        if "error" in b:
            raise RuntimeError(b["error"])

        return b["name"]

    def publish_dir(
        self, scowl_dir: Optional[str] = None, deps_file: Optional[str] = None
    ) -> None:
        """
        Push local scowl dir to branch and promote to LIVE.

        Arguments:
            scowl_dir: Path to .scowl files. Default: `'.'`
            deps_file: Path to deps file [default: <scowl_dir>/deps.scowl]

        """
        scowl_dir = scowl_dir or CONFIG.scowl_dir
        logger.info(f"Publishing dir '{scowl_dir}' to LIVE.")
        branch = self.create_branch_from_dir(scowl_dir, "main", deps_file)
        self.publish_branch(branch)

    def publish_branch(self, branch: Optional[str] = None) -> None:
        """
        Promote branch to LIVE.

        Arguments:
            branch: Specify a branch other than the client default.
        """
        branch = branch or self._branch
        logger.info(f"Publishing '{branch}' branch to LIVE.")
        query = """
            mutation PublishBranch($id: String!) {
                publish(id: $id) {
                    id
                }
            }
        """
        self._execute_graphql(
            query=query,
            variables={"id": branch},
            error_prefix=f"Error publishing branch '{branch}'",
        )

    def publish_scowl(self, scowl: str) -> None:
        """
        Push local scowl source to branch and promote to LIVE.

        Arguments:
            scowl: Scowl source code as string.
        """
        logger.info("Publishing scowl to LIVE.")
        branch = self.create_branch_from_scowl(scowl, "main")
        self.publish_branch(branch)

    def diff_branch_with_live(
        self, branch: Optional[str] = None
    ) -> dict[str, list[str]]:
        """
        Compare branch to LIVE topology and return diff.

        Arguments:
            branch: Specify a source branch other than the client default.

        Returns:
            Events and features added, redefined, and deleted.
        """

        branch = branch or self._branch
        logger.info(f"Diffing '{branch}' branch against LIVE.")
        query = """
            query Branch($id: String!) {
                branch(id: $id) {
                liveDiff {
                    eventsAdded
                    eventsDeleted
                    topologyDiffs {
                        eventType
                        featuresDeleted
                        featuresAdded
                        featuresRedefined
                        featuresDirtied
                    }
                    tableDiffs {
                        id
                        oldVersion
                        newVersion
                    }
                    warnings
                }
              }
            }
        """

        ret = self._execute_graphql(query=query, variables={"id": branch})

        return ret["data"]["branch"]["liveDiff"]

    def get_branches(self) -> list[dict]:
        """
        Return all branches and their metadata.

        Returns:
            Branch metadata.
        """
        logger.debug("Getting branches")
        query = """
            query Branchlist {
                branches {
                    id
                    events
                    error
                    creator
                    lastUpdated
                }
            }
        """

        ret = self._execute_graphql(query=query, error_prefix="error getting branches")

        rows = []
        for branch in ret["data"]["branches"]:
            row = {
                "name": branch["id"],
                "creator": branch["creator"],
                "update_ts": branch["lastUpdated"],
                "event_types": branch["events"],
            }
            if branch["error"]:
                row["error"] = branch["error"]

            rows.append(row)
        return rows

    def get_live_scowl(self) -> str:
        """
        Return scowl source code for LIVE topology as single cleansed string.

        Returns:
            Scowl source code as string.
        """
        query = """
            query LiveScowl {
                liveBranch { scowl }
            }
        """

        ret = self._execute_graphql(query=query)

        scowl = ret["data"]["liveBranch"]["scowl"]
        return scowl

    def delete_branch(self, branch: Optional[str] = None) -> None:
        """
        Delete server-side branch

        Arguments:
            branch: Specify a branch other than the client default.
        """
        branch = branch or self._branch
        logger.info(f"Deleting branch '{branch}'.")
        query = """
            mutation DeleteBranch($id: String!) {
                deleteBranch(id: $id) {
                    id
                }
            }
        """

        self._execute_graphql(
            query=query,
            variables={"id": branch},
            error_prefix=f"Error deleting branch '{branch}'",
        )

    def save_branch_to_dir(
        self,
        scowl_dir: Optional[str] = None,
        branch: Optional[str] = None,
        deps_file: Optional[str] = None,
    ) -> str:
        """
        Save remote branch scowl files to local dir.

        Arguments:
            scowl_dir: Path to save .scowl files.
            branch: Specify a source branch other than the client default.
            deps_file: Path to deps file [default: <scowl_dir>/deps.scowl]

        Returns:
            Name of branch created
        """
        scowl_dir = scowl_dir or CONFIG.scowl_dir
        branch = branch or self._branch
        deps_file = deps_file or os.path.join(scowl_dir, DEPS_FILE)

        logger.info(f"Fetching objects for branch '{branch}''")

        query = """
            query BranchObjects($id: String!) {
                branch(id: $id) {
                    objects {
                        key
                        scowl
                    }
                }
            }
        """

        ret = self._execute_graphql(
            query=query,
            variables={"id": branch},
            error_prefix=f"error getting branch '{branch}'",
        )

        d = ret["data"]["branch"]
        if not d:
            raise ValueError(f"branch '{branch}' not found")

        logger.info(f"Saving branch '{branch}' to dir '{scowl_dir}'")

        for obj in d["objects"]:
            fname = os.path.join(scowl_dir, obj["key"])
            if obj["key"] == DEPS_FILE:
                fname = deps_file
            with open(fname, "w") as f:
                f.write(obj["scowl"])

        return branch

    def get_inputs_from_feed(
        self,
        start_ts: Optional[Union[pendulum.DateTime, str]] = None,
        end_ts: Optional[Union[pendulum.DateTime, str]] = None,
        count: Optional[int] = None,
        event_types: Optional[list[str]] = None,
        where: dict[str, str] = {},
        batch_size: int = 10000,
        ascending: bool = False,
    ) -> list[dict]:
        """
        Return the raw input events from the Event Feed.

        Fetches events in descending time order from `end_ts`. May specify `count` or `start_ts`, but not both.

        Arguments:
            start_ts: Earliest event timestamp to fetch (local client timezone). If not specified, `count` will be used instead.
            end_ts: Latest event timestamp to fetch (local client timezone) [default: now].
            count: Number of rows to return (if start_ts not specified) [default: 10].
            event_types: Subset of event types to fetch. [default: all]
            where: dictionary of equality conditions (all must be true for a match), e.g. {"zipcode": "90210", "email_domain": "gmail.com"}.
            batch_size: Maximum number of records to fetch per GraphQL call.
            ascending: Sort results in ascending chronological order instead of descending.

        Returns:
            list of events: [{"_id": , "_type": , "_time": , [inputs...]}] (in descending time order).
        """

        where = [{"key": k, "value": v} for k, v in where.items()]
        if batch_size < 1 or batch_size > 10000:
            raise RuntimeError(f"batch size: {batch_size} is out of range [1,10000]")
        end_ts = end_ts or str(pendulum.now())
        if isinstance(end_ts, pendulum.DateTime):
            end_ts = str(end_ts)
        end_ts = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )

        if event_types is not None:
            event_types = [{"type": t} for t in event_types]

        query = """
        query EventFeed($size: Int!, $end: DateTime!, $eventTypes: [EventSelection], $where: [FeatureFilter]!, $reverse: Boolean!) {
            events {
                feed(
                    from: 0
                    size: $size
                    end: $end
                    types: $eventTypes
                    where: $where
                    reverse: $reverse
                ) {
                id
                type
                time
                input
                }
            }
        }
        """
        if start_ts:
            if count:
                raise RuntimeError("specify only one of: start_ts or count")
            if isinstance(start_ts, pendulum.DateTime):
                start_ts = str(start_ts)
            start_ts = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
                pendulum.timezone("UTC")
            )

            rows = []
            done = False
            while not done:
                variables = {
                    "size": batch_size,
                    "end": end_ts.to_iso8601_string(),
                    "where": where,
                    "reverse": ascending,
                }
                if event_types:
                    variables["eventTypes"] = event_types
                ret = self._execute_graphql(
                    query=query,
                    variables=variables,
                )
                new_rows = []
                for event in ret["data"]["events"]["feed"]:
                    event_time = pendulum.parse(event["time"])
                    if event_time < start_ts:
                        done = True
                        break
                    row = {
                        "_id": event["id"],
                        "_type": event["type"],
                        "_time": str(event_time),
                    }
                    row.update(event["input"])
                    new_rows.append(row)
                rows.extend(new_rows)
                if done or not new_rows:
                    break
                end_ts = event_time
            return rows
        else:  # count
            if count is None:
                count = 10
            from_ = 0
            rows = []
            while True:
                size = min(batch_size, count - from_)
                if size <= 0:
                    break
                variables = {
                    "size": size,
                    "end": end_ts.to_iso8601_string(),
                    "where": where,
                    "reverse": ascending,
                }
                if event_types:
                    variables["eventTypes"] = event_types
                ret = self._execute_graphql(
                    query=query,
                    variables=variables,
                )
                new_rows = []
                for event in ret["data"]["events"]["feed"]:
                    event_time = pendulum.parse(event["time"])
                    row = {
                        "_id": event["id"],
                        "_type": event["type"],
                        "_time": str(event_time),
                    }
                    row.update(event["input"])
                    new_rows.append(row)
                rows.extend(new_rows)
                from_ += size
                if from_ >= count:
                    break
                end_ts = event_time
            return rows

    def get_features_from_feed(
        self,
        event_type: str,
        start_ts: Optional[Union[pendulum.DateTime, str]] = None,
        end_ts: Optional[Union[pendulum.DateTime, str]] = None,
        count: Optional[int] = None,
        where: dict[str, str] = {},
        batch_size: int = 10000,
        ascending: bool = False,
    ) -> list[dict]:
        """
        For a given event type, return the feature values as they were
        calculated at event time.

        Fetches events in descending time order from `end_ts`. May specify `count` or `start_ts`, but not both.

        Arguments:
            event_type: Event type name.
            start_ts: Earliest event timestamp to fetch (local client timezone). If not specified, `count` will be used instead.
            end_ts: Latest event timestamp to fetch (local client timezone) [default: now].
            count: Number of rows to return (if start_ts not specified) [default: 10].
            where: dictionary of equality conditions (all must be true for a match), e.g. {"zipcode": "90210", "email_domain": "gmail.com"}.
            batch_size: Maximum number of records to fetch per GraphQL call.
            ascending: Sort results in ascending chronological order instead of descending.

        Returns:
            rows: _id, _time, [features...] (in descending time order).
        """

        where = [{"key": k, "value": v} for k, v in where.items()]
        if batch_size < 1 or batch_size > 10000:
            raise RuntimeError(f"batch size: {batch_size} is out of range [1,10000]")
        end_ts = end_ts or str(pendulum.now())
        if isinstance(end_ts, pendulum.DateTime):
            end_ts = str(end_ts)
        end_ts = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )

        query = """
        query EventFeed($size: Int!, $end: DateTime!, $eventType: String!, $where: [FeatureFilter]!, $reverse: Boolean!) {
            events {
                feed(
                    from: 0
                    size: $size
                    end: $end
                    types: [{ type: $eventType, where: $where }]
                    reverse: $reverse
                ) {
                id
                time
                features
                }
            }
        }
        """
        if start_ts:
            if count:
                raise RuntimeError("specify only one of: start_ts or count")
            if isinstance(start_ts, pendulum.DateTime):
                start_ts = str(start_ts)
            start_ts = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
                pendulum.timezone("UTC")
            )

            rows = []
            done = False
            while not done:
                ret = self._execute_graphql(
                    query=query,
                    variables={
                        "size": batch_size,
                        "end": end_ts.to_iso8601_string(),
                        "eventType": event_type,
                        "where": where,
                        "reverse": ascending,
                    },
                )
                new_rows = []
                for event in ret["data"]["events"]["feed"]:
                    event_time = pendulum.parse(event["time"])
                    if event_time < start_ts:
                        done = True
                        break
                    row = {"_id": event["id"], "_time": event_time}
                    row.update(event["features"])
                    new_rows.append(row)
                rows.extend(new_rows)
                if done or not new_rows:
                    break
                end_ts = event_time
            return rows
        else:  # count
            if count is None:
                count = 10
            from_ = 0
            rows = []
            while True:
                size = min(batch_size, count - from_)
                if size <= 0:
                    break
                ret = self._execute_graphql(
                    query=query,
                    variables={
                        "size": size,
                        "end": end_ts.to_iso8601_string(),
                        "eventType": event_type,
                        "where": where,
                        "reverse": ascending,
                    },
                )
                new_rows = []
                for event in ret["data"]["events"]["feed"]:
                    event_time = pendulum.parse(event["time"])
                    row = {"_id": event["id"], "_time": event_time}
                    row.update(event["features"])
                    new_rows.append(row)
                rows.extend(new_rows)
                from_ += size
                if from_ >= count:
                    break
                end_ts = event_time
            return rows

    def get_live_schema(self) -> dict[str, dict[str, str]]:
        """
        Return the feature names and types for every event in the LIVE topology

        Returns:
            dictionary {'event_name': {'f1': 'int', 'f2': 'bool', ...} ...}
        """
        logger.debug("Getting LIVE schema")
        query = """
            query Topology {
                topology(name: "live") {
                    events {
                        name
                        features {
                            name
                            type
                        }
                    }
                }
            }
        """

        ret = self._execute_graphql(
            query=query, error_prefix="error getting live schema"
        )

        events = {}
        for event in ret["data"]["topology"]["events"]:
            events[event["name"]] = {f["name"]: f["type"] for f in event["features"]}

        return events

    def _athena_feature_sql(
        self, event_type, start_ts, end_ts, features, include_inputs, where
    ):
        schema = self.get_live_schema()
        if event_type not in schema:
            raise ValueError(f"event '{event_type}' not found in LIVE topology")

        if features is None:
            features = list(schema[event_type].keys())

        for f in features:
            if f not in schema[event_type]:
                raise ValueError(
                    f"feature '{event_type}.{f}' not found in LIVE topology"
                )

        type_map = {
            "int": "int",
            "bool": "boolean",
            "float": "double",
            "string": "varchar",
            "time": "varchar",
        }

        scalar_selector = """, (case when (json_extract_scalar(features, '$.{}') = 'null') then null
            else try_cast(json_extract_scalar(features, '$.{}') AS {}) end) "{}"
            """

        # Athena doesn't support "timestamp with timezone" for format='PARQUET' so leave as strings
        # time_selector = """, (case when (json_extract_scalar(features, '$.{}') = 'null') then null
        #     else from_iso8601_timestamp(json_extract_scalar(features, '$.{}')) end) "{}"
        #     """

        selector = """, json_format(json_extract(features, '$.{}')) "{}"
            """

        json_fields = []
        selectors = []
        for f, t in schema[event_type].items():
            if t in type_map:
                selectors.append(scalar_selector.format(f, f, type_map[t], f))
            # elif t == "time":
            #    selectors.append(time_selector.format(f, f, f))
            else:
                selectors.append(selector.format(f, f))
                if f in features:
                    json_fields.append(f)

        where = f"where {where}" if where else ""
        inputs = ""
        if include_inputs:
            inputs = ', event as "_inputs"'
            json_fields.append("_inputs")

        features = [f'"{feature}"' for feature in features]
        returned = ", ".join(["_id", "_time"] + features)

        query = f"""with tmp as (
            select
            event_id "_id"
            ,event_ts "_time"
            {inputs}
            {"".join(selectors)}
            from
            "event_log"
            where (event_type = '{event_type}')
            and (event_ts between '{start_ts}' and '{end_ts}')
            ) select {returned} from tmp {where}
            """

        logger.debug(query)
        return query, json_fields

    def get_features_from_log(
        self,
        event_type: str,
        start_ts: Optional[Union[pendulum.DateTime, str]] = None,
        end_ts: Optional[Union[pendulum.DateTime, str]] = None,
        features: Optional[list[str]] = None,
        include_inputs: bool = False,
        where: Optional[str] = None,
        deserialize_json: bool = True,
    ) -> "pd.DataFrame":
        """
        For a given event type, fetch the historical values for features, as
        calculated in the LIVE environment.

        Arguments:
            event_type: Event type name.
            start_ts: Earliest event timestamp to fetch (local client timezone). If not specified, will start from beginning of log.
            end_ts: Latest event timestamp to fetch (local client timezone) [default: now].
            features: Subset of features to fetch. [default: all].
            include_inputs: Include request json as "_inputs" column.
            where: SQL clauses (not including "where" keyword), e.g. "col1 is not null"
            deserialize_json: Deserialize complex data types from JSON strings to Python objects.

        Returns:
            rows: _id, _time, [features...] (in ascending time order).
        """
        end_ts = end_ts or str(pendulum.now())
        if isinstance(end_ts, pendulum.DateTime):
            end_ts = str(end_ts)
        end_ts = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )

        start_ts = start_ts or "1971-01-01"
        if isinstance(start_ts, pendulum.DateTime):
            start_ts = str(start_ts)
        start_ts = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )

        where = (where or "").strip()
        if where.lower().startswith("where"):
            raise ValueError("'where' condition should omit the 'where' keyword")
        sql, json_fields = self._athena_feature_sql(
            event_type, start_ts, end_ts, features, include_inputs, where
        )

        df = self.query_athena(sql)
        if deserialize_json:
            df = df.assign(
                **{field: df[field].apply(json.loads) for field in json_fields}
            )
        return df.set_index("_id")

    def get_timelines(self) -> list[dict]:
        """
        Return all timelines and their metadata.

        Returns:
            Timeline metadata.
        """

        logger.debug("Getting timelines")
        query = """
            query Timelinelist {
                timelines { id, createUser, createTime, metadata { start, end, count, events }, source, state, error }
            }
        """
        ret = self._execute_graphql(query)
        rows = []
        for timeline in ret["data"]["timelines"]:
            status = timeline["state"]
            row = {
                "name": timeline["id"],
                "creator": timeline["createUser"],
                "create_ts": timeline["createTime"],
                "event_types": timeline["metadata"]["events"],
                "event_count": timeline["metadata"]["count"],
                "start_ts": (
                    timeline["metadata"]["start"]
                    if timeline["metadata"]["start"] != "0001-01-01T00:00:00Z"
                    else ""
                ),
                "end_ts": (
                    timeline["metadata"]["end"]
                    if timeline["metadata"]["end"] != "0001-01-01T00:00:00Z"
                    else ""
                ),
                "source": timeline["source"],
                "status": status,
                "error": timeline["error"],
            }
            rows.append(row)
        return rows

    def get_timeline(self, timeline: str) -> dict:
        """
        Return metadata about the timeline.

        Arguments:
            timeline: Timeline name.

        Returns:
            Timeline metadata.
        """
        logger.debug(f"Getting timeline '{timeline}'")
        timelines = self.get_timelines()
        for tl in timelines:
            if tl["name"] == timeline:
                return tl
        raise RuntimeError(f"Timeline '{timeline}' not found.")

    def delete_timeline(self, timeline: str) -> None:
        """
        Delete timeline

        Arguments:
            timeline: Timeline name.
        """
        logger.info(f"Deleting timeline '{timeline}'.")
        query = """
            mutation DeleteTimeline($id: String!) {
                deleteTimeline(id: $id) {
                    id
                }
            }
        """

        self._execute_graphql(query=query, variables={"id": timeline})

    def infer_schema_from_timeline(self, timeline: str) -> str:
        """
        Attempt to infer the paths and data types of all fields in the timeline's
        input data. Generate the scowl to parse all JSON paths.

        This function helps bootstrap scowl code for new event types, with
        the expectation that most feature names will need to be modified.

        e.g.
        ```
            account_id := $.account.id as int
            purchase_items_0_amount := $.purchase.items[0].amount as float
        ```

        Arguments:
            timeline: Timeline name.

        Returns:
            Scowl source code as string.
        """
        query = """
            query TimelineScowl($id: String!) {
                timeline(id: $id) { id, scowl }
            }
        """

        ret = self._execute_graphql(query=query, variables={"id": timeline})

        return ret["data"]["timeline"]["scowl"]

    def create_timeline_from_s3(
        self,
        timeline: str,
        s3_uri: str,
        time_path: str,
        data_path: str,
        id_path: Optional[str] = None,
        type_path: Optional[str] = None,
        default_type: Optional[str] = None,
    ):
        """
        Create (or overwrite) timeline from a JSON file on S3

        Arguments:
            timeline: Timeline name.
            s3_uri: S3 bucket URI.
            time_path: JSON path where event timestamp is found (e.g. $._time)
            data_path: JSON path where event payload is found (e.g. $)
            id_path: JSON path where event ID is found (e.g. $.event_id)
            type_path: JSON path where event type is found (e.g. $._type)
            default_type: Event type to use in case none found at `type_path`
        """
        query = """
            mutation SaveTimelineMutation($id: String!, $source: String!, $state: String!, $parameters: [KeyValueInput]!) {
                saveTimeline(id: $id, source: $source, state: $state, parameters: $parameters) {
                    id
                }
            }
        """

        parameters = [
            {"key": "s3_uri", "value": s3_uri},
            {"key": "time_path", "value": time_path},
            {"key": "data_path", "value": data_path},
        ]

        if default_type:
            parameters.append({"key": "default_type", "value": default_type})

        if id_path:
            parameters.append({"key": "id_path", "value": id_path})

        if type_path:
            parameters.append({"key": "type_path", "value": type_path})

        ret = self._execute_graphql(
            query=query,
            variables={
                "id": timeline,
                "source": "s3",
                "state": "processing",
                "parameters": parameters,
            },
        )

        return ret["data"]["saveTimeline"]["id"]

    def create_timeline_from_log(
        self,
        timeline: str,
        start_ts: Union[pendulum.DateTime, str],
        end_ts: Union[pendulum.DateTime, str],
        event_types: Optional[list[str]] = None,
    ) -> None:
        """
        Create (or overwrite) timeline from the Event Log

        Arguments:
            timeline: Timeline name.
            start_ts: Earliest event timestamp to fetch (local client timezone).
            end_ts: Latest event timestamp to fetch (local client timezone).
            event_types: Event types to include (default: all).
        """

        query = """
            mutation SaveTimeline($id: String!, $parameters: [KeyValueInput]!) {
              saveTimeline(id: $id, source: "athena", state: "processing", parameters: $parameters) {
                id
              }
            }
        """
        if isinstance(start_ts, pendulum.DateTime):
            start_ts = str(start_ts)
        if isinstance(end_ts, pendulum.DateTime):
            end_ts = str(end_ts)
        start_ts = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )
        end_ts = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )
        start_str = start_ts.to_iso8601_string()
        end_str = end_ts.to_iso8601_string()
        parameters = [
            {"key": "start", "value": start_str},
            {"key": "end", "value": end_str},
        ]

        if event_types:
            events = ",".join(event_types)
            parameters.append({"key": "events", "value": events})

        self._execute_graphql(
            query=query, variables={"id": timeline, "parameters": parameters}
        )
        self._wait_for_timeline_processing(timeline)

    def create_timeline_from_dataframes(
        self,
        timeline: str,
        df_dict: dict,
    ) -> None:
        """
        Create (or overwrite) timeline from a collection of DataFrames—one per event type.

        Arguments:
            timeline: Timeline name.
            df_dict: Dictionary from event type name to DataFrame of events.
        """
        import pandas as pd

        time_dfs = []
        for event_type, df in df_dict.items():
            if "_time" not in df.columns:
                raise ValueError(
                    f"DataFrame for event type '{event_type}' must have '_time' column"
                )
            time_dfs.append(df[["_time"]].assign(_type=event_type))
        combined = pd.concat(time_dfs)
        combined.sort_values("_time", inplace=True)

        jsonl = ""
        for index, time_row in combined.iterrows():
            row = df_dict[time_row["_type"]].loc[index].copy()
            row["_type"] = time_row["_type"]
            jsonl += row.to_json(date_format="iso") + "\n"
        return self.create_timeline_from_jsonl(timeline, jsonl)

    def create_timeline_from_jsonl(self, timeline: str, jsonl: str) -> None:
        """
        Create (or overwrite) timeline from JSON events passed in as a string.

        Arguments:
            timeline: Timeline name.
            jsonl: JSON event data, one JSON dict per line.
        """

        if not jsonl.endswith("\n"):
            jsonl += "\n"
        data = gzip.compress(bytes(jsonl, "utf-8"))
        self._create_timeline_from_jsonl_gz(timeline, data)

    def _create_timeline_from_jsonl_gz(
        self,
        timeline: str,
        data: bytes,
    ) -> None:
        query = """
            mutation SaveTimelineMutation($id: String!,
                                          $filename: String!) {
                saveTimeline(id: $id, source: "file", state: "new") {
                    uploadUrl(name: $filename)
                }
            }
        """

        ret = self._execute_graphql(
            query=query, variables={"id": timeline, "filename": "timeline.jsonl.gz"}
        )

        url = ret["data"]["saveTimeline"]["uploadUrl"]

        http_response = requests.put(url, data=data)
        if http_response.status_code != 200:
            raise RuntimeError(http_response.error)

        query = """
            mutation SaveTimelineMutation($id: String!) {
                saveTimeline(id: $id, source: "file", state: "processing") {
                    id
                }
            }
        """

        ret = self._execute_graphql(query=query, variables={"id": timeline})

        self._wait_for_timeline_processing(timeline)

    def _wait_for_timeline_processing(self, timeline: str) -> None:
        RETRIES = 180
        DELAY = 5.0
        retry_count = 0
        while retry_count < RETRIES:
            tl = self.get_timeline(timeline)
            if tl["status"] != "processing":
                if tl["status"] != "materialized":
                    raise RuntimeError(
                        f"unexpected timeline state: {tl['status']} error: {tl['error']}"
                    )
                return
            time.sleep(DELAY)
            retry_count += 1
        if self.status == "processing":
            raise RuntimeError(f"Timed out after {DELAY * RETRIES} seconds")

    def create_timeline_from_file(self, timeline: str, filename: str) -> None:
        """
        Create (or overwrite) timeline from events stored in a file.

        Supported file types: `.jsonl`, `.jsonl.gz`

        Arguments:
            timeline: Timeline name.
            filename: Name of events file to upload.
        """

        _, ext = splitext(filename)

        if ext in (".jsonl.gz", ".json.gz"):
            with open(filename, "rb") as f:
                self._create_timeline_from_jsonl_gz(timeline, f.read())
        elif ext in (".jsonl", ".json"):
            with open(filename, "r") as f:
                jsonl = f.read()
                self.create_timeline_from_jsonl(timeline, jsonl)
        else:
            raise RuntimeError(f"Unsupported file extension: {ext}")

    def get_materialization(self, id: str) -> Materialization:
        return Materialization(self, id)

    def replay(
        self,
        features: list[str],
        start_ts: Union[pendulum.DateTime, str],
        end_ts: Union[pendulum.DateTime, str],
        extra_timelines: Optional[list[str]] = None,
        branch: Optional[str] = None,
    ) -> Materialization:
        """
        Recompute historical feature values from LIVE event log on given topology branch.

        This is the primary function of the SDK.

        Arguments:
            features: list of features to materialize, e.g. `['login.email', 'purchase.*']`
            start_ts: Earliest event timestamp to materialize (local client timezone).
            end_ts: Latest event timestamp to materialize (local client timezone).
            extra_timelines: Names of supplemental timelines.
            branch: Specify a source branch other than the client default.

        Returns:
            Handle to Materialization job
        """

        if isinstance(start_ts, pendulum.DateTime):
            start_ts = str(start_ts)
        start = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )
        start = int(start.timestamp())

        if isinstance(end_ts, pendulum.DateTime):
            end_ts = str(end_ts)
        end = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )
        end = int(end.timestamp())

        live_timeline = f"live_{start}_{end}"
        create_timeline = True
        try:
            tl = self.get_timeline(live_timeline)
            create_ts = pendulum.parse(tl["create_ts"]).timestamp()
            if create_ts > end:
                create_timeline = False
        except RuntimeError:
            pass
        if create_timeline:
            self.create_timeline_from_log(live_timeline, start_ts, end_ts)
        timelines = (extra_timelines or []) + [live_timeline]
        return self.materialize(timelines, features, start_ts, end_ts, branch)

    def materialize(
        self,
        timelines: list[str],
        features: list[str] = None,
        start_ts: Optional[Union[pendulum.DateTime, str]] = None,
        end_ts: Optional[Union[pendulum.DateTime, str]] = None,
        branch: Optional[str] = None,
    ) -> Materialization:
        """
        Enrich collection of timelines using topology at branch. Timelines are merged based on timestamp.

        Arguments:
            timelines: Timeline names.
            features: list of features to materialize, e.g. `['login.email', 'purchase.*']`
            start_ts: Earliest event timestamp to materialize (local client timezone).
            end_ts: Latest event timestamp to materialize (local client timezone).
            branch: Specify a source branch other than the client default.

        Returns:
            Handle to Materialization job
        """
        variables = {
            "timelines": timelines,
            "branch": branch or self._branch,
            "features": features,
        }

        if start_ts:
            if isinstance(start_ts, pendulum.DateTime):
                start_ts = str(start_ts)
            start_ts = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
                pendulum.timezone("UTC")
            )
            variables["start"] = start_ts.to_iso8601_string()

        if end_ts:
            if isinstance(end_ts, pendulum.DateTime):
                end_ts = str(end_ts)
            end_ts = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
                pendulum.timezone("UTC")
            )
            variables["end"] = end_ts.to_iso8601_string()

        query = """
            mutation DistributedMaterialize($timelines: [String], $branch: String!, $features: [String], $start: DateTime, $end: DateTime) {
                distributedMaterialize(timelines: $timelines, branch: $branch, features: $features, start: $start, end: $end) { id }
            }        
        """

        ret = self._execute_graphql(
            query=query,
            variables=variables,
        )

        return Materialization(self, ret["data"]["distributedMaterialize"]["id"])

    def get_models(self) -> list[dict]:
        """
        Return all models and their metadata.

        Returns:
            Model metadata.
        """
        logger.debug("Getting models")
        query = """
            query Modellist {
                models {
                    nodes {
                        name
                        liveVersion {
                            version
                        }
                        latestVersion {
                            version
                        }
                        updatedAt
                        updatedBy
                    }
                }
            }
        """

        ret = self._execute_graphql(query=query, error_prefix="error getting models")

        rows = []
        for model in ret["data"]["models"]["nodes"]:
            live_version = (
                model["liveVersion"]["version"] if model["liveVersion"] else ""
            )
            row = {
                "name": model["name"],
                "live_version": live_version,
                "latest_version": model["latestVersion"]["version"],
                "update_ts": model["updatedAt"],
                "updated_by": model["updatedBy"],
            }
            rows.append(row)
        return rows

    def get_model_history(self, name: str) -> list[dict]:
        """
        Return list of versions for the given model along with their metadata.

        Arguments:
            name: Model name.

        Returns:
            Model version metadata.
        """

        query = """
            query ModelVersions($name: String!) {
                model(name: $name) {
                    versions {
                        nodes {
                            version
                            status
                            createdAt
                            creator
                        }
                    }
                }
            }
        """

        ret = self._execute_graphql(
            query=query,
            variables={"name": name},
            error_prefix=f"error getting versions of model '{name}'",
        )

        rows = []
        for version in ret["data"]["model"]["versions"]["nodes"]:
            row = {
                "version": version["version"],
                "status": humanize_status(version["status"]),
                "create_ts": version["createdAt"],
                "created_by": version["creator"],
            }
            rows.append(row)
        return rows

    def get_model_version(self, name: str, version: str) -> ModelVersion:
        """
        Return handle to a specific model version.

        Arguments:
            name: Model name.
            version: Model version.

        Returns:
            Model version future object.
        """
        return ModelVersion(self, name, version)

    def get_model_schema(self, name: str, version: Optional[str] = None) -> str:
        if version is None:
            for model in self.get_models():
                if model["name"] == name:
                    version = model["latest_version"]
                    break
            else:
                raise RuntimeError(f"model '{name}' not found")
        return self.get_model_version(name, version).schema

    def _get_model_version(self, name: str, version: str) -> dict[str, Any]:
        query = """
            query GetModelVersion($name: String!, $version: String!) {
                modelVersion(name: $name, version: $version) {
                    status
                    error
                    s3Uri
                    uploadUrl
                    creator
                    createdAt
                    updatedAt
                    size
                    inputSchema
                    outputSchema
                    scowlSnippet
                    metadata
                    comment
                }
            }
        """
        ret = self._execute_graphql(
            query=query,
            variables={"name": name, "version": version},
        )

        return ret["data"]["modelVersion"]

    def _create_empty_model_version(
        self, model: str, s3_uri: Optional[str] = None, comment: Optional[str] = None
    ) -> tuple[str, str]:
        query = """
            mutation ModelVersionPath($name: String!, $s3Uri: String, $comment: String) {
                createEmptyModelVersion(name: $name, s3Uri: $s3Uri, comment: $comment) {
                    version
                    s3Uri
                    uploadUrl
                }
            }
        """

        variables = {"name": model}
        if s3_uri:
            variables["s3Uri"] = s3_uri
        if comment:
            variables["comment"] = comment
        ret = self._execute_graphql(query=query, variables=variables)

        version = ret["data"]["createEmptyModelVersion"]["version"]
        upload_url = ret["data"]["createEmptyModelVersion"]["uploadUrl"]

        return version, upload_url

    def _load_model_version(self, model: str, version: str) -> None:
        query = """
            mutation LoadModelVersion($name: String!, $version: String!) {
                loadModelVersion(name: $name, version: $version) {
                    status
                    error
                }
            }
        """

        variables = {"name": model, "version": version}
        ret = self._execute_graphql(query=query, variables=variables)

        status = ret["data"]["loadModelVersion"]["status"]
        error = ret["data"]["loadModelVersion"]["error"]
        if status != "Online":
            raise RuntimeError(f"Model status after load was {status}: {error}")

    def create_model_from_pmml(
        self, model: str, filename: str, comment: Optional[str] = None
    ) -> str:
        """
        Create (or overwrite) model from PMML file.

        Arguments:
            model: Model name, e.g. "churn_predictor".
            filename: Local PMML file, e.g. "my_model.xml"
            comment: A comment string to store with the model version. Max 60 characters. Optional

        Returns:
            A `ModelVersion` handle to the upload job.
        """

        with open(filename, "rb") as f:
            version, upload_uri = self._create_empty_model_version(
                model, comment=comment
            )

            files = {"file": (filename, f)}
            http_response = requests.put(upload_uri, files=files)
            if http_response.status_code != 200:
                raise RuntimeError(http_response.error)

        self._load_model_version(model, version)

        return ModelVersion(self, model, version)

    def get_models_openai(self) -> list[dict]:
        """
        Return all OpenAI models and their metadata.

        Returns:
            OpenAI Model metadata.
        """
        logger.debug("Getting openai models")
        query = """
            query OpenAIModellist {
                integration(type: "openai") {
                    type
                    creator
                    createdAt
                    updatedBy
                    updatedAt
                    error
                    status
                    output
                }
            }
        """

        try:
            ret = self._execute_graphql(query=query)
        except RuntimeError as e:
            if str(e) == "could not find resource 'openai'":
                return []
            raise

        integration = ret["data"]["integration"]
        if integration["status"] == "Error":
            raise RuntimeError(f"OpenAI integration error: {integration['error']}")

        rows = []
        output = integration.get("output") or {}
        for model in output.get("models", []):
            row = {
                "name": model["id"],
                "owner": model["owner"],
                "type": model["type"],
            }
            rows.append(row)
        return rows

    def get_openai_config(self) -> dict:
        """
        Return the current OpenAI model configuration, if any

        Returns:
            OpenAI Model configuration state.
        """
        logger.debug("Getting openai config")
        query = """
            query OpenAIConfig {
                integration(type: "openai") {
                    creator
                    createdAt
                    updatedBy
                    updatedAt
                    error
                    status
                    config
                }
            }
        """

        try:
            ret = self._execute_graphql(query=query)
        except RuntimeError as e:
            if str(e) == "could not find resource 'openai'":
                return None
            raise

        return ret["data"]["integration"]

    def set_openai_config(
        self,
        api_key: str,
        timeout_ms: int = None,
        retry_limit: int = None,
        max_tokens: int = None,
    ) -> dict:
        """
        Create or update OpenAI model configuration

        Arguments:
            api_key: OpenAI API key
            timeout_ms: Timeout in milliseconds. Default 5000
            retry_limit: Number of retries to perform on API error. Default 3
            max_tokens: Maximum number of tokens to generate in a single request. Default 8192

        Returns:
            OpenAI Model configuration state.
        """
        logger.debug("Setting openai config")
        if timeout_ms is None:
            timeout_ms = 5000
        if retry_limit is None:
            retry_limit = 3
        if max_tokens is None:
            max_tokens = 8192

        current_config = self.get_openai_config()
        mutation = (
            "createIntegration" if current_config is None else "updateIntegration"
        )

        query = f"""
            mutation OpenAIConfig($config: JSON) {{
                {mutation}(type: "openai", config: $config) {{
                    creator
                    createdAt
                    updatedBy
                    updatedAt
                    error
                    status
                    config
                }}
            }}
        """

        ret = self._execute_graphql(
            query=query,
            variables={
                "config": {
                    "apiKey": api_key,
                    "timeoutMs": timeout_ms,
                    "retryLimit": retry_limit,
                    "maxTokens": max_tokens,
                }
            },
        )

        return ret["data"][mutation]

    def delete_openai_config(self) -> None:
        """
        Delete the current OpenAI configuration
        """
        logger.debug("Deleting openai config")

        query = """
            mutation DeleteOpenAIConfig {
                deleteIntegration(type: "openai") {
                    type
                }
            }
        """

        self._execute_graphql(query=query)

    def refresh_openai_config(self) -> dict:
        """
        Refresh the OpenAI model list using the existing configuration

        Returns:
            OpenAI Model configuration state.
        """
        logger.debug("Refreshing openai config")

        query = """
            mutation RefreshOpenAI {
                testIntegration(type: "openai") {
                    creator
                    createdAt
                    updatedBy
                    updatedAt
                    error
                    status
                    config
                }
            }
        """

        ret = self._execute_graphql(query=query)

        return ret["data"]["testIntegration"]

    def version(self) -> str:
        """
        Return the server-side version number.

        Returns:
            Version identifier
        """
        query = """
            query Version {
                version
            }
        """

        ret = self._execute_graphql(query=query)

        return ret["data"]["version"]

    def get_deps(self, live: bool = False) -> str:
        """
        Fetch latest dependencies from server as Scowl source `require` statements.

        Arguments:
            live: Return the LIVE versions of dependencies instead of latest.

        Returns:
            Scowl source code as string.
        """
        if live:
            raise NotImplementedError("option to fetch LIVE deps not yet supported")
        table_entries = []
        model_entries = []
        for row in self.get_tables():
            table_entries.append(f"  {row['name']} {row['latest_version']}")
        for row in self.get_models():
            model_entries.append(f"  {row['name']} {row['latest_version']}")
        final = ""
        if table_entries:
            joined = "\n".join(table_entries)
            final = f"require table (\n{joined}\n)\n"
        if model_entries:
            joined = "\n".join(model_entries)
            final += f"require model (\n{joined}\n)\n"
        return final

    def save_deps(self, live: bool = False, deps_file: Optional[str] = None) -> str:
        """
        Fetch latest dependencies from server and save to file

        Arguments:
            live: Return the LIVE versions of dependencies instead of latest.
            deps_file: Path to save deps file [default: ./deps.scowl]

        Returns:
            Full path to saved dependency file.
        """

        deps = self.get_deps(live)
        deps_file = deps_file or DEPS_FILE
        with open(deps_file, "w") as f:
            f.write(deps + "\n")
        return deps_file

    def resolve_deps_from_file(self, deps_file: Optional[str] = None) -> str:
        """
        Return the resolved resources (i.e. table schemas) from the local `deps.scowl` file.

        Arguments:
            deps_file: Path to deps file [default: ./deps.scowl]

        Returns:
            Resolved resource definitions (table schemas) as scowl code.
        """

        deps_file = deps_file or DEPS_FILE
        try:
            with open(deps_file, "r") as f:
                return self.resolve_deps(f.read())
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Could not find '{deps_file}'. Try running `sumatra deps update` first."
            )

    def resolve_deps(self, requires: str) -> str:
        """
        Return the resolved resources (i.e. table schemas) from the given requires statements.

        Arguments:
            requires: Scowl requires statement as code blob

        Returns:
            Resolved resource definitions (table schemas) as scowl code.
        """
        query = """
            query Deps($deps: String!) {
                resolveDeps(deps: $deps)
            }
        """
        ret = self._execute_graphql(
            query=query,
            variables={"deps": requires},
        )

        return ret["data"]["resolveDeps"]

    def get_tables(self) -> list[dict]:
        """
        Return all tables and their metadata.

        Returns:
            Table metadata.
        """
        logger.debug("Getting tables")
        query = """
            query Tablelist {
                tables {
                    nodes {
                        name
                        liveVersion {
                            version
                        }
                        latestVersion {
                            version
                        }
                        updatedAt
                        updatedBy
                    }
                }
            }
        """

        ret = self._execute_graphql(query=query, error_prefix="error getting tables")

        rows = []
        for table in ret["data"]["tables"]["nodes"]:
            live_version = (
                table["liveVersion"]["version"] if table["liveVersion"] else ""
            )
            row = {
                "name": table["name"],
                "live_version": live_version,
                "latest_version": table["latestVersion"]["version"],
                "update_ts": table["updatedAt"],
                "updated_by": table["updatedBy"],
            }
            rows.append(row)
        return rows

    def get_table_schema(self, name: str, version: Optional[str] = None) -> str:
        if version is None:
            for table in self.get_tables():
                if table["name"] == name:
                    version = table["latest_version"]
                    break
            else:
                raise RuntimeError(f"table '{name}' not found")
        return self.get_table_version(name, version).schema

    def get_table_history(self, name: str) -> list[dict]:
        """
        Return list of versions for the given table along with their metadata.

        Arguments:
            name: Table name.

        Returns:
            DataFrame of version metadata.
        """

        query = """
            query TableVersions($name: String!) {
                table(name: $name) {
                    versions {
                        nodes {
                            version
                            rowCount
                            status
                            createdAt
                            creator
                        }
                    }
                }
            }
        """

        ret = self._execute_graphql(
            query=query,
            variables={"name": name},
            error_prefix=f"error getting versions of table '{name}'",
        )

        rows = []
        for version in ret["data"]["table"]["versions"]["nodes"]:
            row = {
                "version": version["version"],
                "row_count": version["rowCount"],
                "status": humanize_status(version["status"]),
                "create_ts": version["createdAt"],
                "created_by": version["creator"],
            }
            rows.append(row)
        return rows

    def get_table_version(self, name: str, version: str) -> TableVersion:
        """
        Return handle to a specific table version.

        Arguments:
            name: Table name.
            version: Table version.

        Returns:
            Table version future object.
        """
        return TableVersion(self, name, version)

    def _get_table_version(self, name: str, version: str) -> dict[str, Any]:
        query = """
            query GetTableVersion($name: String!, $version: String!) {
                tableVersion(name: $name, version: $version) {
                    status
                    error
                    s3Uri
                    creator
                    createdAt
                    updatedAt
                    schema
                    rowCount
                    jobId
                    key
                }
            }
        """
        ret = self._execute_graphql(
            query=query,
            variables={"name": name, "version": version},
        )
        return ret["data"]["tableVersion"]

    def _create_empty_table_version(
        self, table: str, s3_uri: Optional[str] = None
    ) -> tuple[str, str]:
        query = """
            mutation TableVersionPath($name: String!, $s3Uri: String) {
                createEmptyTableVersion(name: $name, s3Uri: $s3Uri) {
                    version
                    s3Uri
                }
            }
        """

        variables = {"name": table}
        if s3_uri:
            variables["s3Uri"] = s3_uri
        ret = self._execute_graphql(query=query, variables=variables)

        version = ret["data"]["createEmptyTableVersion"]["version"]
        s3_uri = ret["data"]["createEmptyTableVersion"]["s3Uri"]
        return version, s3_uri

    def create_table_from_dataframe(
        self,
        table: str,
        df: "pd.DataFrame",
        key_column: str,
        include_index: bool = False,
    ) -> TableVersion:
        """
        Create (or overwrite) table from a DataFrame

        Arguments:
            table: Table name.
            df: DataFrame to upload as table
            key_column: Name of column containing the prmary index for the table
            include_index: Include the DataFrame's index as a column named `index`?

        Returns:
            A `TableVersion` handle to the upload job.
        """
        MAX_ROWS_PER_FILE = 1000000

        try:
            import awswrangler as wr
        except ImportError:
            raise ImportError(
                "awswrangler is required for Pandas DataFrame support. "
                "Install with: pip install awswrangler"
            )

        if len(df) == 0:
            raise ValueError("non-empty dataframe required for table creation")
        if key_column not in df.columns:
            raise ValueError(
                f"key column '{key_column}' not found in column list: {df.columns.tolist()}"
            )
        if df[key_column].isnull().sum() > 0:
            raise ValueError(
                f"key column {key_column} contained missing or null values"
            )
        if df[key_column].nunique() != len(df):
            raise ValueError(f"key column {key_column} did not contain unique values")

        if not TABLE_NAME_REGEXP.match(table):
            raise ValueError(f"invalid table name '{table}'")
        for column in df.columns:
            if not TABLE_NAME_REGEXP.match(column):
                raise ValueError(f"invalid table field name '{column}'")

        version, s3_uri = self._create_empty_table_version(table)

        wr.s3.to_parquet(
            boto3_session=self.boto,
            df=df,
            compression="snappy",
            path=s3_uri,
            dataset=True,
            index=include_index,
            bucketing_info=([key_column], (len(df) // MAX_ROWS_PER_FILE + 1)),
            concurrent_partitioning=True,
            pyarrow_additional_kwargs={
                "coerce_timestamps": "ms",
                "allow_truncated_timestamps": True,
                "use_deprecated_int96_timestamps": False,
            },
            mode="overwrite",
        )
        row_count = len(df)

        return self._create_table_from_s3(table, s3_uri, key_column, row_count, version)

    def _create_table_from_s3(
        self,
        table: str,
        s3_uri: str,
        key_column: str,
        expected_row_count: int,
        version: Optional[str] = None,
    ) -> TableVersion:
        if version is None:
            version, _ = self._create_empty_table_version(table, s3_uri)

        create_table_query = """
            mutation CreateTable($name: String!, $version: String!, $key: String!, $rowCount: Int!) {
                loadTableVersion(name: $name, version: $version, key: $key, rowCount: $rowCount) {
                    status
                }
            }
        """
        self._execute_graphql(
            query=create_table_query,
            variables={
                "name": table,
                "version": version,
                "key": key_column,
                "rowCount": expected_row_count,
            },
        )

        return TableVersion(self, table, version)

    def delete_table_version(self, table: str, version: str) -> None:
        """
        Delete a specific version of a table permanently.

        If the table version is referenced in the LIVE topology, it cannot be deleted.

        Arguments:
            table: Table name.
            version: Version identifier.
        """
        query = """
            mutation DeleteTableVersion($name: String!, $version: String!) {
                deleteTableVersion(name: $name, version: $version) {
                    name
                    version
                }
            }
        """
        self._execute_graphql(
            query=query,
            variables={
                "name": table,
                "version": version,
            },
        )

    def delete_table(self, table: str) -> None:
        """
        Delete a table permanently.

        If the table is referenced in the LIVE topology, it cannot be deleted.

        Arguments:
            table: Table name.
        """
        query = """
            mutation DeleteTable($name: String!) {
                deleteTable(name: $name) {
                    name
                }
            }
        """
        self._execute_graphql(
            query=query,
            variables={
                "name": table,
            },
        )

    def delete_model_version(self, model: str, version: str) -> None:
        """
        Delete a specific version of a model permanently.

        If the model version is referenced in the LIVE topology, it cannot be deleted.

        Arguments:
            model: Model name.
            version: Version identifier.
        """
        query = """
            mutation DeleteModelVersion($name: String!, $version: String!) {
                deleteModelVersion(name: $name, version: $version) {
                    name
                    version
                }
            }
        """
        self._execute_graphql(
            query=query,
            variables={
                "name": model,
                "version": version,
            },
        )

    def delete_model(self, model: str) -> None:
        """
        Delete a model permanently.

        If the model is referenced in the LIVE topology, it cannot be deleted.

        Arguments:
            model: Model name.
        """
        query = """
            mutation DeleteModel($name: String!) {
                deleteModel(name: $name) {
                    name
                }
            }
        """
        self._execute_graphql(
            query=query,
            variables={
                "name": model,
            },
        )

    def get_event_counts(
        self,
        start_ts: Union[pendulum.DateTime, str],
        end_ts: Union[pendulum.DateTime, str],
        event_types: Optional[list[str]] = None,
    ) -> dict[str, int]:
        """
        Return the number of events from CloudWatch logs in the given time range.

        Arguments:
            start_ts: Earliest event timestamp to count (local client timezone).
            end_ts: Latest event timestamp to count (local client timezone).
            event_types: List of event types to include. If None, include all event types in LIVE topology.
        """
        return self._get_metric(
            "TotalTime", "sampleCount", start_ts, end_ts, event_types=event_types
        )

    def get_error_counts(
        self,
        start_ts: Union[pendulum.DateTime, str],
        end_ts: Union[pendulum.DateTime, str],
        event_types: Optional[list[str]] = None,
    ) -> dict[str, int]:
        """
        Return the number of errors from CloudWatch logs in the given time range.

        Arguments:
            start_ts: Earliest event timestamp to count (local client timezone).
            end_ts: Latest event timestamp to count (local client timezone).
            event_types: List of event types to include. If None, include all event types in LIVE topology.
        """
        return self._get_metric(
            "EventErrors", "sum", start_ts, end_ts, event_types=event_types
        )

    def _get_metric(
        self,
        metric_name: str,
        stat_name: str,
        start_ts: Union[pendulum.DateTime, str],
        end_ts: Union[pendulum.DateTime, str],
        event_types: Optional[list[str]] = None,
    ) -> dict[str, int]:
        if isinstance(start_ts, pendulum.DateTime):
            start_ts = str(start_ts)
        if isinstance(end_ts, pendulum.DateTime):
            end_ts = str(end_ts)
        start = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )
        start = start.to_iso8601_string()

        end = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )
        end = end.to_iso8601_string()

        if event_types is None:
            event_types = self.get_live_schema().keys()

        metrics = []
        for event_type in event_types:
            metrics.append(
                f"""
                {event_type}: metrics(
                    end: $end
                    namespace: $namespace
                    metric: "{metric_name}"
                    start: $start
                    dimensions: [{{
                        name: "EventType"
                        value: "{event_type}"
                    }}]
                ) {{
                    stats {{
                        {stat_name}
                    }}
                }}
            """
            )
        query = (
            "query Metric($namespace: String!, $start: DateTime!, $end: DateTime!) {"
            + "\n".join(metrics)
            + "}"
        )
        namespace = f"Sumatra/{self.workspace_id}/Realtime"
        ret = self._execute_graphql(
            query=query,
            variables={"start": start, "end": end, "namespace": namespace},
        )

        counts = {}
        for event_type, res in ret["data"].items():
            if res["stats"]:
                counts[event_type] = res["stats"][stat_name]
            else:
                counts[event_type] = 0

        return counts

    def list_users(self) -> list[dict]:
        """
        list all of the users in this workspace

        Returns:
            A dataframe of the users and their metadata
        """

        query = """
            query getUsers($after: String) {
                currentTenant {
                    userRoles(first: 100, after: $after) {
                        nodes {
                            email
                            role
                            createdAt
                            updatedAt
                            creator
                            tenantSlug
                        }
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                    }
                }
            }
        """

        variables = {"after": None}
        has_next_page = True
        rows = []

        while has_next_page:
            ret = self._execute_graphql(
                query=query,
                variables=variables,
            )

            for d in ret["data"]["currentTenant"]["userRoles"]["nodes"]:
                rows.append(
                    {
                        "email": d["email"],
                        "role": d["role"],
                        "create_ts": d["createdAt"],
                        "update_ts": d["updatedAt"],
                        "creator": d["creator"],
                        "tenant": d["tenantSlug"],
                    }
                )
            has_next_page = ret["data"]["currentTenant"]["userRoles"]["pageInfo"][
                "hasNextPage"
            ]
            variables["after"] = ret["data"]["currentTenant"]["userRoles"]["pageInfo"][
                "endCursor"
            ]
        return rows

    def invite_user(
        self,
        email: str,
        role: str,
        resend_email: bool = True,
        app: Optional[str] = None,
    ) -> dict:
        """
        Invite a user to this workspace, with the given role.

        Arguments:
            email: The user's email address
            role: The desired role for the user. One of {'owner', 'publisher', 'writer', 'reader'}
            resend_email: If True, resend the invitation email if the user has already been invited to Sumatra
            app: The name of the app to invite the user to ('optimize' or None)

        Returns:
            A dict of the user's metadata
        """

        query = """
            mutation tenantCreateUser($email: String!, $role: String!, $resendEmail: Boolean, $app: String) {
                tenantCreateUser(email: $email, role: $role, sendInvite: $resendEmail, app: $app) {
                    email
                    role
                    createdAt
		            updatedAt
		            creator
		            tenantSlug
                }
            }
        """

        if app is not None and app != "optimize":
            raise ValueError(f"Unknown app '{app}'.")

        ret = self._execute_graphql(
            query=query,
            variables={
                "email": email,
                "role": role,
                "resendEmail": resend_email,
                "app": app,
            },
        )

        d = ret["data"]["tenantCreateUser"]
        return {
            "email": d["email"],
            "role": d["role"],
            "create_ts": pendulum.parse(d["createdAt"]),
            "update_ts": pendulum.parse(d["updatedAt"]),
            "creator": d["creator"],
            "tenant": d["tenantSlug"],
        }

    def remove_user(self, email: str) -> dict:
        """
        Remove a user from this workspace

        Arguments:
            email: The user's email address

        Returns:
            A dict of the user's metadata
        """

        query = """
            mutation tenantDeleteUser($email: String!) {
                tenantDeleteUser(email: $email) {
                    email
                    role
                    createdAt
		            updatedAt
		            creator
		            tenantSlug
                }
            }
        """

        ret = self._execute_graphql(query=query, variables={"email": email})

        d = ret["data"]["tenantDeleteUser"]
        return {
            "email": d["email"],
            "role": d["role"],
            "create_ts": pendulum.parse(d["createdAt"]),
            "update_ts": pendulum.parse(d["updatedAt"]),
            "creator": d["creator"],
            "tenant": d["tenantSlug"],
        }

    def set_user_role(self, email: str, role: str) -> dict:
        """
        Set a user's role within this workspace.

        Note that the user must already be a member of the workspace. You can use `invite_user` to add a new user.

        Arguments:
            email: The user's email address
            role: The desired role for the user. One of {'owner', 'publisher', 'writer', 'reader'}

        Returns:
            A dict of the user's metadata
        """

        query = """
            mutation tenantSetUserRole($email: String!, $role: String!) {
                tenantSetUserRole(email: $email, role: $role) {
                    email
                    role
                    createdAt
		            updatedAt
		            creator
		            tenantSlug
                }
            }
        """

        ret = self._execute_graphql(
            query=query, variables={"email": email, "role": role}
        )

        d = ret["data"]["tenantSetUserRole"]
        return {
            "email": d["email"],
            "role": d["role"],
            "create_ts": pendulum.parse(d["createdAt"]),
            "update_ts": pendulum.parse(d["updatedAt"]),
            "creator": d["creator"],
            "tenant": d["tenantSlug"],
        }
