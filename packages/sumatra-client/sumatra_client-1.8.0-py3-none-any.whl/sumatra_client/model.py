import pendulum
from typing import Optional
from sumatra_client.util import humanize_status


class ModelVersion:
    """
    A handle to a versioned model resource
    """

    def __init__(self, client, name: str, version: str):
        self._client = client
        self._name = name
        self._version = version
        self._mv = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def __repr__(self) -> str:
        return f"ModelVersion(name='{self.name}', version='{self.version}', status='{self.status}')"

    def _get_model_version(self):
        return self._client._get_model_version(self.name, self.version)

    @property
    def status(self) -> str:
        """
        Current status of the job. One of {'Processing', 'Ready', 'Error'}
        """
        self._mv = self._get_model_version()
        return humanize_status(self._mv["status"])

    @property
    def schema(self) -> str:
        """
        Scowl schema of the model
        """
        if not self._mv:
            self._mv = self._get_model_version()
        return self._mv["inputSchema"]

    @property
    def error(self) -> Optional[str]:
        """
        Error reason string for a failed upload.
        """
        if not self._mv:
            self._mv = self._get_model_version()
        return self._mv["error"]

    @property
    def s3_uri(self) -> str:
        """
        S3 bucket path to PMML file
        """
        if not self._mv:
            self._mv = self._get_model_version()
        return self._mv["s3Uri"]

    @property
    def creator(self) -> str:
        """
        User that initiated the model upload
        """
        if not self._mv:
            self._mv = self._get_model_version()
        return self._mv["creator"]

    @property
    def created_at(self) -> pendulum.DateTime:
        """
        Timestamp when model version was created
        """
        if not self._mv:
            self._mv = self._get_model_version()
        return pendulum.parse(self._mv["createdAt"])

    @property
    def updated_at(self) -> pendulum.DateTime:
        """
        Timestamp when model version was last updated
        """
        if not self._mv:
            self._mv = self._get_model_version()
        return pendulum.parse(self._mv["updatedAt"])

    @property
    def comment(self) -> str:
        """
        Comment from when the model version was uploaded
        """
        if not self._mv:
            self._mv = self._get_model_version()
        return self._mv["comment"]

    @property
    def scowl_snippet(self) -> str:
        """
        Example usage of the model version
        """
        if not self._mv:
            self._mv = self._get_model_version()
        return self._mv["scowlSnippet"]

    @property
    def metadata(self) -> str:
        """
        PMML metadata of the model version
        """
        if not self._mv:
            self._mv = self._get_model_version()
        return self._mv["metadata"]
