import logging
from time import sleep
from tqdm.auto import tqdm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger("sumatra.materialization")


class Materialization:
    """
    A handle to a server-side materialization (replay) job, which enriches a Timeline
    (or set of Timelines) by running it (them) through a given Topology.

    Objects are not constructed directly. Materializations are returned by methods
    of the `Client` class.
    """

    def __init__(self, client, id):
        self._client = client
        self.id = id
        self._mtr = None

    def __repr__(self):
        return f"Materialization(id='{self.id}')"

    def _get_materialization(self):
        query = """
            query Materialization($id: String!) {
                materialization(id: $id) { id, state, path, timelines, events, branch, hash, jobsSubmitted, jobsCompleted, timelineKeys { name, key } }
            }
        """

        ret = self._client._execute_graphql(query=query, variables={"id": self.id})

        return ret["data"]["materialization"]

    def status(self) -> str:
        """
        Current status of the job. One of {'processing', 'materialized', 'error'}
        """
        self._mtr = self._get_materialization()
        return self._mtr["state"]

    def wait(self) -> str:
        """
        Wait until materialization completes. In a Notebook, a progress bar is displayed.

        Returns:
            Materialization status
        """

        self._mtr = self._get_materialization()
        if self._mtr["state"] not in ["new", "processing", "materialized"]:
            raise RuntimeError(f"Error in {self}: {self._mtr['state']}")

        # Do not show progress bars if already materialized
        if self._mtr["state"] == "materialized":
            return self._mtr["state"]

        while self._mtr["jobsSubmitted"] == 0 and self._mtr["state"] in [
            "new",
            "processing",
        ]:
            sleep(0.5)
            self._mtr = self._get_materialization()

        submitted = self._mtr["jobsSubmitted"]
        completed = self._mtr["jobsCompleted"]

        with tqdm(total=submitted) as pbar:
            pbar.update(completed)
            while self._mtr["state"] == "processing":
                sleep(0.5)
                self._mtr = self._get_materialization()
                new_completed = self._mtr["jobsCompleted"]
                new_submitted = self._mtr["jobsSubmitted"]
                if new_submitted != submitted:
                    pbar.total = new_submitted
                    submitted = new_submitted

                pbar.update(new_completed - completed)
                completed = new_completed
            if self._mtr["state"] == "materialized":
                pbar.update(submitted - completed)

        return self._mtr["state"]

    def progress(self) -> str:
        """
        Current progress of subjobs: X of Y jobs completed.
        """
        self._mtr = self._get_materialization()

        if self._mtr["state"] != "processing":
            return self._mtr["state"]
        else:
            completed = self._mtr["jobsCompleted"]
            submitted = self._mtr["jobsSubmitted"]
            return f"{completed} / {submitted} jobs completed."

    @property
    def timelines(self) -> list[str]:
        """
        Timelines materialized by the job.
        """
        if self._mtr is None:
            self._mtr = self._get_materialization()
        return list(sorted(self._mtr["timelines"]))

    @property
    def timeline_keys(self) -> list[str]:
        """
        Timeline keys for each feature to support querying from cache
        """
        if self._mtr is None:
            self._mtr = self._get_materialization()
        return self._mtr["timelineKeys"]

    @property
    def event_types(self) -> list[str]:
        """
        Materialized event types
        """
        if self._mtr is None:
            self._mtr = self._get_materialization()
        return list(sorted(self._mtr["events"]))

    @property
    def branch(self) -> str:
        """
        Topology branch used for materialization.
        """
        if self._mtr is None:
            self._mtr = self._get_materialization()
        return self._mtr["branch"]

    @property
    def hash(self) -> str:
        """
        Unique hash identifying the job.
        """
        if self._mtr is None:
            self._mtr = self._get_materialization()
        return self._mtr["hash"]

    @property
    def path(self) -> str:
        """
        S3 bucket path where results are stored.
        """
        self.wait()
        return self._mtr["path"]

    def get_features(self, event_type: str, features: list[str] = []) -> "pd.DataFrame":
        """
        Return feature values for given event type. Waits if
        job is still processing.

        Arguments:
            event_type: Name of event type to fetch.
            features: Feature names to fetch. By default, fetch all.

        Returns:
            Feature dataframe
        """
        try:
            import awswrangler as wr
        except ImportError:
            raise ImportError(
                "awswrangler is required for Pandas DataFrame support. "
                "Install with: pip install awswrangler"
            )

        self.wait()
        path = f"{self.path}/events/event_type={event_type}/"
        cols = ["_id", "_type", "_time"]
        cols.extend(features)

        if not features:
            df = wr.s3.read_parquet(
                boto3_session=self._client.boto,
                path=path,
                use_threads=8,
            )
        else:
            df = wr.s3.read_parquet(
                boto3_session=self._client.boto,
                path=path,
                columns=cols,
                use_threads=8,
            )

        return df.set_index("_id")

    def get_errors(self, event_type: str, features: list[str] = []) -> "pd.DataFrame":
        """
        Return event-level materialization errors for specified event type. Waits if
        job is still processing.

        Arguments:
            event_type: Name of event type to fetch.
            features: Feature names to fetch. By default, fetch all.

        Returns:
            Event-level errors
        """
        try:
            import awswrangler as wr
        except ImportError:
            raise ImportError(
                "awswrangler is required for Pandas DataFrame support. "
                "Install with: pip install awswrangler"
            )
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for Pandas DataFrame support. "
                "Install with: pip install pandas"
            )

        self.wait()
        path = f"{self.path}/errors/event_type={event_type}/"
        cols = ["_id", "_type", "_time"]
        cols.extend(features)

        try:
            if not features:
                df = wr.s3.read_parquet(
                    boto3_session=self._client.boto,
                    path=path,
                    ignore_empty=True,
                )
            else:
                df = wr.s3.read_parquet(
                    boto3_session=self._client.boto,
                    path=path,
                    columns=cols,
                    ignore_empty=True,
                )
        except Exception as e:
            logger.debug(e)
            return pd.DataFrame(columns=cols)

        return df.set_index("_id")
