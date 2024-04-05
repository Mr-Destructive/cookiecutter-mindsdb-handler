from typing import List

from mindsdb_sql import Select, Insert, CreateTable, Delete
from mindsdb_sql.parser.ast.base import ASTNode

from mindsdb.integrations.libs.response import (
    RESPONSE_TYPE,
    HandlerResponse as Response,
    HandlerStatusResponse as StatusResponse,
)

{% if cookiecutter.handler_type == 'mlengine' %}
from mindsdb.integrations.libs.base import BaseMLEngine as Handler
{% elif cookiecutter.handler_type == 'api' %}
from mindsdb.integrations.libs.api_handler import APIHandler as Handler
{% else %}
from mindsdb.integrations.libs.base import DatabaseHandler as Handler


from mindsdb.utilities import log

logger = log.getLogger(__name__)


class {{ cookiecutter.handler_name }}Handler(Handler):
    """This handler handles connection and execution of the {{ cookiecutter.handler_name }}."""

    name = "{{ cookiecutter.handler_name }}"

    def __init__(self, name: str, **kwargs):
        super().__init__(name)

        self._connection_data = kwargs.get("connection_data")

        self._client = None
        self.is_connected = False
        self.connect()

    def _get_client(self):
        return self._connection_data

    def __del__(self):
        if self.is_connected is True:
            self.disconnect()

    def connect(self):
        if self.is_connected is True:
            return self._client

        try:
            self._client = self._get_client()
            self.is_connected = True
            return self._client
        except Exception as e:
            logger.error(f"Error connecting to client, {e}!")
            self.is_connected = False

    def disconnect(self):
        if self.is_connected is False:
            return

        self._client = None
        self.is_connected = False

    def check_connection(self):
        response_code = StatusResponse(False)
        return response_code

    def query(self, query: ASTNode) -> Response:

        if isinstance(query, Select):
            return self.select(
                query.table_name,
                query.columns,
                query.conditions,
                query.offset,
                query.limit,
            )
        elif isinstance(query, Insert):
            return self.insert(query.table_name, query.fields, query.values)
        elif isinstance(query, CreateTable):
            return self.create_table(query.table_name)
        elif isinstance(query, Delete):
            return self.delete_document(query.table_name, query.conditions)
        else:
            return Response(resp_type=RESPONSE_TYPE.ERROR, error_message="Invalid query")

    def select(
        self,
        table_name: str,
        columns: List[str] = None,
        conditions: List[str] = None,
        offset: int = None,
        limit: int = None,
    ) -> dict:
        select = Select(table_name)
        if columns:
            select.columns = columns
        if conditions:
            select.conditions = conditions
        if offset:
            select.offset = offset
        if limit:
            select.limit = limit
        return self._client.query(select)


