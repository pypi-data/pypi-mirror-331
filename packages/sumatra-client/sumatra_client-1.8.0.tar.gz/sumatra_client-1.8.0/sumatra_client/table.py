import time
import pendulum
from typing import Optional
from sumatra_client.util import humanize_status


class TableVersion:
    """
    A handle to a server-side table upload job, which uploads a new table version.

    Objects are not constructed directly. Table versions are returned by methods
    of the `Client` class.
    """

    def __init__(self, client, name: str, version: str):
        self._client = client
        self._name = name
        self._version = version
        self._tv = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def __repr__(self) -> str:
        return f"TableVersion(name='{self.name}', version='{self.version}', status='{self.status}')"

    def _get_table_version(self):
        return self._client._get_table_version(self.name, self.version)

    @property
    def status(self) -> str:
        """
        Current status of the job. One of {'New', 'Offline', 'Online', 'Error'}
        """
        self._tv = self._get_table_version()
        return humanize_status(self._tv["status"])

    @property
    def error(self) -> Optional[str]:
        """
        Error reason string for a failed upload.
        """
        if not self._tv:
            self._tv = self._get_table_version()
        return self._tv["error"]

    def wait(self) -> str:
        """
        Wait until table version upload completes.

        Returns:
            Table version upload status
        """

        expected_status = "Ready"
        while self.status not in [expected_status, "Error"]:
            time.sleep(0.5)

        final_status = self.status
        if final_status != expected_status:
            raise RuntimeError(
                f"Table creation failed, status {final_status}, error {self.error}"
            )
        return final_status

    @property
    def s3_uri(self) -> str:
        """
        S3 bucket path to parquet file
        """
        if not self._tv:
            self._tv = self._get_table_version()
        return self._tv["s3Uri"]

    @property
    def creator(self) -> str:
        """
        User that initiated the table version job
        """
        if not self._tv:
            self._tv = self._get_table_version()
        return self._tv["creator"]

    @property
    def created_at(self) -> pendulum.DateTime:
        """
        Timestamp when table version was created
        """
        if not self._tv:
            self._tv = self._get_table_version()
        return pendulum.parse(self._tv["createdAt"])

    @property
    def updated_at(self) -> pendulum.DateTime:
        """
        Timestamp when table version was last updated
        """
        if not self._tv:
            self._tv = self._get_table_version()
        return pendulum.parse(self._tv["updatedAt"])

    @property
    def schema(self) -> str:
        """
        Scowl table statement with schema
        """
        if not self._tv:
            self._tv = self._get_table_version()
        return self._tv["schema"]

    @property
    def row_count(self) -> int:
        """
        Number of rows in table
        """
        if not self._tv:
            self._tv = self._get_table_version()
        return self._tv["rowCount"]

    @property
    def job_id(self) -> str:
        """
        Job indentifier for validation and ingest
        """
        if not self._tv:
            self._tv = self._get_table_version()
        return self._tv["jobId"]

    @property
    def key(self) -> str:
        """
        Name of primary index column
        """
        if not self._tv:
            self._tv = self._get_table_version()
        return self._tv["key"]
