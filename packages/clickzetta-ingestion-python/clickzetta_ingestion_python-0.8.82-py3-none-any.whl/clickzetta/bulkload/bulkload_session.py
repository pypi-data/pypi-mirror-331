from typing import Any, Dict, Optional, Union

from clickzetta.bulkload import bulkload_api
from clickzetta.bulkload.bulkload_stream import BulkLoadStream
from clickzetta.connector.v0.client import Client


class Session:
    class SessionBuilder:
        def __init__(self) -> None:
            self._options = {}

        def _remove_config(self, key: str) -> "Session.SessionBuilder":
            self._options.pop(key, None)
            return self

        def config(self, key: str, value: Union[int, str]) -> "Session.SessionBuilder":
            self._options[key] = value
            return self

        def configs(
            self, options: Dict[str, Union[int, str]]
        ) -> "Session.SessionBuilder":
            self._options = {**self._options, **options}
            return self

        def create(self) -> "Session":
            session = self._create_internal(self._options.get("url"))
            return session

        def _create_internal(self, conn: str = None) -> "Session":
            new_session = Session(
                conn,
                self._options,
            )
            return new_session

        def __get__(self, obj, objtype=None):
            return Session.SessionBuilder()

    builder: SessionBuilder = SessionBuilder()

    def __init__(self, conn: str, options: Optional[Dict[str, Any]] = None) -> None:
        self._client = Client(cz_url=conn)

    def create_bulkload_stream(self, schema_name: str, table_name: str, options):
        bulkload_meta_data = bulkload_api.create_bulkload_stream_metadata(
            self._client, schema_name, table_name, options
        )
        return BulkLoadStream(bulkload_meta_data, self._client)

    def commit_bulkload_stream(
        self,
        instance_id: int,
        workspace: str,
        schema_name: str,
        table_name: str,
        stream_id: str,
        execute_workspace: str,
        execute_vc: str,
        commit_mode,
    ):
        return bulkload_api.commit_bulkload_stream(
            self._client,
            instance_id,
            workspace,
            schema_name,
            table_name,
            stream_id,
            execute_workspace,
            execute_vc,
            commit_mode,
        )

    def get_bulkload_stream(self, schema_name: str, table_name: str, stream_id: str):
        bulkload_meta_data = bulkload_api.get_bulkload_stream(
            self._client, schema_name, table_name, stream_id
        )
        return BulkLoadStream(bulkload_meta_data, self._client)

    def close(self):
        return
