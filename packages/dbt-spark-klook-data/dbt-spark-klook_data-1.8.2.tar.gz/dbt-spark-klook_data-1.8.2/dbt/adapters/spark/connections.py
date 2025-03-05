import json
import os
from contextlib import contextmanager
from time import sleep

from dbt.adapters.contracts.connection import (
    AdapterResponse,
    ConnectionState,
    Connection,
    Credentials,
)
from dbt.adapters.events.logging import AdapterLogger
from dbt.adapters.exceptions import FailedToConnectError
from dbt.adapters.sql import SQLConnectionManager
from dbt_common.exceptions import DbtConfigError, DbtRuntimeError, DbtDatabaseError

from dbt_common.utils.encoding import DECIMALS
import requests

from dbt.adapters.spark import __version__

try:
    from TCLIService.ttypes import TOperationState as ThriftState
    from thrift.transport import THttpClient
    from pyhive import hive
except ImportError:
    ThriftState = None
    THttpClient = None
    hive = None
try:
    import pyodbc
except ImportError:
    pyodbc = None
from datetime import datetime
import sqlparams
from dbt_common.dataclass_schema import StrEnum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union, Tuple, List, Generator, Iterable, Sequence

from abc import ABC, abstractmethod

try:
    from thrift.transport.TSSLSocket import TSSLSocket
    import thrift
    import ssl
    import thrift_sasl
    from puresasl.client import SASLClient
except ImportError:
    pass  # done deliberately: setting modules to None explicitly violates MyPy contracts by degrading type semantics

import base64
import time

from alibabacloud_emr_serverless_spark20230808.client import Client
from alibabacloud_emr_serverless_spark20230808.models import Tag, JobDriverSparkSubmit, JobDriver, StartJobRunRequest, \
    GetJobRunRequest, CancelJobRunRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util import models as util_models

import boto3
from urllib.parse import urlparse

logger = AdapterLogger("Spark")

NUMBERS = DECIMALS + (int, float)


def _build_odbc_connnection_string(**kwargs: Any) -> str:
    return ";".join([f"{k}={v}" for k, v in kwargs.items()])


class SparkConnectionMethod(StrEnum):
    THRIFT = "thrift"
    HTTP = "http"
    ODBC = "odbc"
    SESSION = "session"
    SERVERLESS_SPARK = "serverless_spark"


@dataclass
class SparkCredentials(Credentials):
    host: Optional[str] = None
    schema: Optional[str] = None  # type: ignore
    method: SparkConnectionMethod = None  # type: ignore
    database: Optional[str] = None  # type: ignore
    driver: Optional[str] = None
    cluster: Optional[str] = None
    endpoint: Optional[str] = None
    token: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    port: int = 443
    auth: Optional[str] = None
    kerberos_service_name: Optional[str] = None
    organization: str = "0"
    connect_retries: int = 0
    connect_timeout: int = 10
    use_ssl: bool = False
    server_side_parameters: Dict[str, str] = field(default_factory=dict)
    retry_all: bool = False
    ak: str = None
    sk: str = None
    region: str = "cn-hangzhou"
    workspace_id: str = None

    @classmethod
    def __pre_deserialize__(cls, data: Any) -> Any:
        data = super().__pre_deserialize__(data)
        if "database" not in data:
            data["database"] = None
        return data

    @property
    def cluster_id(self) -> Optional[str]:
        return self.cluster

    def __post_init__(self) -> None:
        if self.method is None:
            raise DbtRuntimeError("Must specify `method` in profile")
        if self.host is None:
            raise DbtRuntimeError("Must specify `host` in profile")
        if self.schema is None:
            raise DbtRuntimeError("Must specify `schema` in profile")

        # spark classifies database and schema as the same thing
        if self.database is not None and self.database != self.schema:
            raise DbtRuntimeError(
                f"    schema: {self.schema} \n"
                f"    database: {self.database} \n"
                f"On Spark, database must be omitted or have the same value as"
                f" schema."
            )
        self.database = None

        if self.method == SparkConnectionMethod.ODBC:
            try:
                import pyodbc  # noqa: F401
            except ImportError as e:
                raise DbtRuntimeError(
                    f"{self.method} connection method requires "
                    "additional dependencies. \n"
                    "Install the additional required dependencies with "
                    "`pip install dbt-spark[ODBC]`\n\n"
                    f"ImportError({e.msg})"
                ) from e

        if self.method == SparkConnectionMethod.ODBC and self.cluster and self.endpoint:
            raise DbtRuntimeError(
                "`cluster` and `endpoint` cannot both be set when"
                f" using {self.method} method to connect to Spark"
            )

        if (
                self.method == SparkConnectionMethod.HTTP
                or self.method == SparkConnectionMethod.THRIFT
        ) and not (ThriftState and THttpClient and hive):
            raise DbtRuntimeError(
                f"{self.method} connection method requires "
                "additional dependencies. \n"
                "Install the additional required dependencies with "
                "`pip install dbt-spark[PyHive]`"
            )

        if self.method == SparkConnectionMethod.SESSION:
            try:
                import pyspark  # noqa: F401
            except ImportError as e:
                raise DbtRuntimeError(
                    f"{self.method} connection method requires "
                    "additional dependencies. \n"
                    "Install the additional required dependencies with "
                    "`pip install dbt-spark[session]`\n\n"
                    f"ImportError({e.msg})"
                ) from e

        if self.method != SparkConnectionMethod.SESSION and self.method != SparkConnectionMethod.SERVERLESS_SPARK:
            self.host = self.host.rstrip("/")

        self.server_side_parameters = {
            str(key): str(value) for key, value in self.server_side_parameters.items()
        }

    @property
    def type(self) -> str:
        return "spark"

    @property
    def unique_field(self) -> str:
        return self.host  # type: ignore

    def _connection_keys(self) -> Tuple[str, ...]:
        return "host", "port", "cluster", "endpoint", "schema", "organization"


class SparkConnectionWrapper(ABC):

    @abstractmethod
    def cursor(self) -> "SparkConnectionWrapper":
        pass

    @abstractmethod
    def cancel(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

    @abstractmethod
    def fetchall(self) -> Optional[List]:
        pass

    @abstractmethod
    def execute(self, sql: str, bindings: Optional[List[Any]] = None) -> None:
        pass

    @property
    @abstractmethod
    def description(
            self,
    ) -> Sequence[
        Tuple[str, Any, Optional[int], Optional[int], Optional[int], Optional[int], bool]
    ]:
        pass

    ######################################################
    #### 实现 Spark 读写锁的逻辑
    LOCK_URL = 'https://onedata.klook.top/v1/dp/gateway/proxy/sparksrv/spark_sql_lock'
    OUTPUT_TABLE_KEY = "output_table"
    INPUT_TABLES_KEY = "input_tables"
    LOCK_TABLES_KEY = "lock_tables"
    DBT_TMP_SUFFIX = "__dbt_tmp"
    _ENV_ = os.getenv("DAGSTER_ENV", "")
    _REGION_ = os.getenv("DAGSTER_REGION", "")

    def not_prod(self):
        return self._ENV_.lower() != 'prod'

    def not_cn(self):
        return self._REGION_.lower() != 'cn'

    def assert_source_table_succeed(self, sql, is_split=False):
        if self.not_prod() or self.not_cn():
            return

        timeout = 30 * 60
        start = datetime.now()

        while (datetime.now() - start).seconds < timeout:
            parse_result = self.parse_sql_table(sql, is_split)
            # 无锁表可以运行
            lock_tables_ = parse_result[self.LOCK_TABLES_KEY]
            if len(lock_tables_) == 0:
                return parse_result
            output_table = None
            if self.OUTPUT_TABLE_KEY in parse_result:
                output_table = parse_result[self.OUTPUT_TABLE_KEY]
            logger.info(f"output_table: {output_table} Locked Tables: {lock_tables_}")
            sleep(30)

        raise Exception("Source table is not ready!!!")

    def update_parser_result(self, parse_result, parse_result_tmp, key_):
        parse_result[key_] = parse_result[key_] + [name for name in parse_result_tmp[key_] if
                                                   not name.endswith(self.DBT_TMP_SUFFIX)]

    def parse_sql_table(self, sql, is_split=False):
        from sqlparse import parse
        # 增量表，create temporary view 和 insert into 合并为一条 SQL，需要切分
        parsed = parse(sql)
        sql_list = [str(stmt).strip() for stmt in parsed if stmt]

        if len(sql_list) > 1 and is_split:
            parse_result = dict()
            parse_result[self.INPUT_TABLES_KEY] = []
            parse_result[self.LOCK_TABLES_KEY] = []
            output_table = None
            for sql in sql_list:
                parse_result_tmp = self.parse_single_sql_table(sql)
                if parse_result is None:
                    raise Exception(f"Spark Sql Parse service is invalid!!! \n {sql}")

                if self.OUTPUT_TABLE_KEY in parse_result_tmp and not parse_result_tmp[self.OUTPUT_TABLE_KEY].endswith(
                        self.DBT_TMP_SUFFIX):
                    output_table = parse_result_tmp[self.OUTPUT_TABLE_KEY]

                self.update_parser_result(parse_result, parse_result_tmp, self.INPUT_TABLES_KEY)
                self.update_parser_result(parse_result, parse_result_tmp, self.LOCK_TABLES_KEY)
            parse_result[self.OUTPUT_TABLE_KEY] = output_table
        else:
            parse_result = self.parse_single_sql_table(sql)
            if parse_result is None:
                raise Exception(f"Spark Sql Parse service is invalid!!! \n {sql}")
        return parse_result

    def parse_single_sql_table(self, sql):
        if self.not_prod() or self.not_cn():
            return

        retry_times = 1
        while retry_times <= 3:
            is_parse_syntax_error = False
            try:
                url = f"{self.LOCK_URL}/parse_table"
                response = requests.post(url, data=sql, headers={'Content-Type': 'text/plain'})
                return self.handle_response(url, response)
            except Exception as e:
                if "[PARSE_SYNTAX_ERROR]" in str(e) or "[UNSUPPORTED_DATATYPE]" in str(e):
                    raise DbtDatabaseError(e)
                    logger.warning(f"[WARNING]parse_sql_table error, try {retry_times}: %s", e)

            sleep(10)
        return None

    def do_release_request(self, url, msg):
        if self.not_prod() or self.not_cn():
            return

        is_succeed = False
        retry_times = 1
        while retry_times <= 3:
            try:
                response = requests.get(url, timeout=60, verify=False)
                self.handle_response(url, response)
                is_succeed = True
                break
            except Exception as e:
                logger.warning(f"[WARNING]{msg} error, try {1}: %s", e)
                sleep(2)

            retry_times += 1
        return is_succeed

    def do_get_request(self, url, msg):
        if self.not_prod() or self.not_cn():
            return

        retry_times = 1
        while retry_times <= 3:
            try:
                response = requests.get(url, timeout=60, verify=False)
                return self.handle_response(url, response)
            except Exception as e:
                logger.warning(f"[WARNING]{msg} error, try {1}: %s", e)
                sleep(2)
            retry_times += 1
        return None

    def catch_locks(self, parse_result):
        if self.not_prod() or self.not_cn():
            return

        if self.OUTPUT_TABLE_KEY not in parse_result:
            return

        output_table_ = parse_result[self.OUTPUT_TABLE_KEY]
        input_tables_ = parse_result[self.INPUT_TABLES_KEY]

        is_write_locked = False
        is_read_locked = True
        # 非 dbt_tmp 表添加 locks，dbt_tmp 添加的 locks 由其下游加锁
        if not output_table_.endswith(self.DBT_TMP_SUFFIX):
            # 添加 WRITE lock
            is_write_locked = self.do_get_request(
                f"{self.LOCK_URL}/lock?table={output_table_}&lockedBy={output_table_}&lockType=WRITE",
                f"WRITE lock {output_table_} error"
            )

            if is_write_locked:
                logger.debug(f"WRITE Locked {output_table_} by {output_table_}")

            # 添加 READ lock
            for in_table in input_tables_:
                if not in_table.endswith(self.DBT_TMP_SUFFIX):
                    lock_result = self.do_get_request(
                        f"{self.LOCK_URL}/lock?table={in_table}&lockedBy={output_table_}&lockType=READ",
                        f"READ lock {in_table} error")
                    if lock_result:
                        logger.debug(f"READ Locked {in_table} by {output_table_}")

                    is_read_locked = is_read_locked and lock_result
                else:
                    # 加 dbt_tmp view source READ lock
                    dbt_tmp_result = self.do_get_request(f"{self.LOCK_URL}/dbt_tmp?dbt_tmp={in_table}",
                                                         f"Fetch {in_table} source table error")
                    if dbt_tmp_result is not None:
                        tmp_input_tables = dbt_tmp_result[self.INPUT_TABLES_KEY]
                        for tmp_input_table in tmp_input_tables:
                            if tmp_input_table == output_table_:
                                # 自己引用自己的其他分区
                                continue

                            lock_result = self.do_get_request(
                                f"{self.LOCK_URL}/lock?table={tmp_input_table}&lockedBy={in_table}",
                                f"READ lock {tmp_input_table} error"
                            )
                            is_read_locked = is_read_locked and lock_result
                            if lock_result:
                                logger.debug(f"READ Locked {tmp_input_table} by {in_table}")
        else:
            logger.debug(f"Temporary View {output_table_} not catch locks, locks will be caught by down stream")
        return is_read_locked and is_write_locked

    def release_locks(self, parse_result):
        if self.not_prod() or self.not_cn() or parse_result is None:
            return

        if self.OUTPUT_TABLE_KEY not in parse_result:
            return

        output_table_ = parse_result[self.OUTPUT_TABLE_KEY]
        input_tables_ = parse_result[self.INPUT_TABLES_KEY]

        # 非 dbt_tmp 表释放 locks，dbt_tmp 添加的 locks 由其下游释放
        if not output_table_.endswith(self.DBT_TMP_SUFFIX):
            release_result = self.do_get_request(
                f"{self.LOCK_URL}/release?table={output_table_}&lockedBy={output_table_}",
                f"Release WRITE lock {output_table_} error")
            if release_result:
                logger.debug(f"Released WRITE Locked {output_table_} by {output_table_}")

            # 释放 READ lock
            for in_table in input_tables_:
                if not in_table.endswith(self.DBT_TMP_SUFFIX):
                    release_result = self.do_get_request(
                        f"{self.LOCK_URL}/release?table={in_table}&lockedBy={output_table_}",
                        f"Release {output_table_} READ lock {in_table} error"
                    )
                    if release_result:
                        logger.debug(f"Released READ Locked {in_table} by {output_table_}")
                else:
                    # 释放 dbt_tmp view source READ lock
                    dbt_tmp_result = self.do_get_request(f"{self.LOCK_URL}/dbt_tmp?dbt_tmp={in_table}",
                                                         f"Fetch {in_table} source table error")
                    if dbt_tmp_result is not None:
                        tmp_input_tables = dbt_tmp_result[self.INPUT_TABLES_KEY]
                        for tmp_input_table in tmp_input_tables:
                            if tmp_input_table == output_table_:
                                # 自己引用自己的其他分区
                                continue

                            release_result = self.do_get_request(
                                f"{self.LOCK_URL}/release?table={tmp_input_table}&lockedBy={in_table}",
                                f"Release {in_table} READ lock {tmp_input_table} error"
                            )
                            if release_result:
                                logger.debug(f"Released READ Lock {tmp_input_table} by {in_table}")
        else:
            logger.debug(f"Temporary View {output_table_} not release locks, locks will be released by down stream")

    def handle_response(self, url: str, response) -> str:
        if response.status_code != 200:
            raise Exception(f"get request, url:{url}, failed. status code:{response.status_code}, text:{response.text}")
        if not response.json()["success"]:
            raise Exception(f"get request, url:{url}, failed. reason:{json.loads(response.text)['error']['message']}")

        result = json.loads(response.text)["result"]
        logger.debug("result: {}", result)
        return result
    ######################################################


class PyhiveConnectionWrapper(SparkConnectionWrapper):
    """Wrap a Spark connection in a way that no-ops transactions"""

    # https://forums.databricks.com/questions/2157/in-apache-spark-sql-can-we-roll-back-the-transacti.html  # noqa

    handle: "pyodbc.Connection"
    _cursor: "Optional[pyodbc.Cursor]"

    def __init__(self, handle: "pyodbc.Connection") -> None:
        self.handle = handle
        self._cursor = None
        self.lock_url = 'https://admin97.fat.klook.io/v1/mercurybatchworkssrv/spark_sql_lock'  ######################################################
        self.parse_result = None

    def cursor(self) -> "PyhiveConnectionWrapper":
        self._cursor = self.handle.cursor()
        return self

    def cancel(self) -> None:
        if self._cursor:
            # Handle bad response in the pyhive lib when
            # the connection is cancelled
            try:
                self._cursor.cancel()
            except EnvironmentError as exc:
                logger.debug("Exception while cancelling query: {}".format(exc))
        self.release_locks(self.parse_result)

    def close(self) -> None:
        if self._cursor:
            # Handle bad response in the pyhive lib when
            # the connection is cancelled
            try:
                self._cursor.close()
            except EnvironmentError as exc:
                logger.debug("Exception while closing cursor: {}".format(exc))
        self.handle.close()
        self.release_locks(self.parse_result)

    def rollback(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("NotImplemented: rollback")

    def fetchall(self) -> List["pyodbc.Row"]:
        assert self._cursor, "Cursor not available"
        return self._cursor.fetchall()

    def execute(self, sql: str, bindings: Optional[List[Any]] = None) -> None:
        if sql.strip().endswith(";"):
            sql = sql.strip()[:-1]

        # Reaching into the private enumeration here is bad form,
        # but there doesn't appear to be any way to determine that
        # a query has completed executing from the pyhive public API.
        # We need to use an async query + poll here, otherwise our
        # request may be dropped after ~5 minutes by the thrift server
        STATE_PENDING = [
            ThriftState.INITIALIZED_STATE,
            ThriftState.RUNNING_STATE,
            ThriftState.PENDING_STATE,
        ]

        STATE_SUCCESS = [
            ThriftState.FINISHED_STATE,
        ]

        if bindings is not None:
            bindings = [self._fix_binding(binding) for binding in bindings]

        assert self._cursor, "Cursor not available"

        ######################################################
        self.parse_result = self.assert_source_table_succeed(sql)
        self.catch_locks(self.parse_result)
        ######################################################
        try:
            self._cursor.execute(sql, bindings, async_=True)

            poll_state = self._cursor.poll()
            state = poll_state.operationState

            while state in STATE_PENDING:
                logger.debug("Poll status: {}, sleeping".format(state))

                poll_state = self._cursor.poll()
                state = poll_state.operationState

            # If an errorMessage is present, then raise a database exception
            # with that exact message. If no errorMessage is present, the
            # query did not necessarily succeed: check the state against the
            # known successful states, raising an error if the query did not
            # complete in a known good state. This can happen when queries are
            # cancelled, for instance. The errorMessage will be None, but the
            # state of the query will be "cancelled". By raising an exception
            # here, we prevent dbt from showing a status of OK when the query
            # has in fact failed.
            if poll_state.errorMessage:
                logger.debug("Poll response: {}".format(poll_state))
                logger.debug("Poll status: {}".format(state))
                raise DbtDatabaseError(poll_state.errorMessage)

            elif state not in STATE_SUCCESS:
                status_type = ThriftState._VALUES_TO_NAMES.get(state, "Unknown<{!r}>".format(state))
                raise DbtDatabaseError("Query failed with status: {}".format(status_type))

            logger.debug("Poll status: {}, query complete".format(state))
        finally:
            self.release_locks(self.parse_result)  ######################################################

    @classmethod
    def _fix_binding(cls, value: Any) -> Union[float, str]:
        """Convert complex datatypes to primitives that can be loaded by
        the Spark driver"""
        if isinstance(value, NUMBERS):
            return float(value)
        elif isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        else:
            return value

    @property
    def description(
            self,
    ) -> Sequence[
        Tuple[str, Any, Optional[int], Optional[int], Optional[int], Optional[int], bool]
    ]:
        assert self._cursor, "Cursor not available"
        return self._cursor.description


class PyodbcConnectionWrapper(PyhiveConnectionWrapper):
    def execute(self, sql: str, bindings: Optional[List[Any]] = None) -> None:
        assert self._cursor, "Cursor not available"
        if sql.strip().endswith(";"):
            sql = sql.strip()[:-1]
        # pyodbc does not handle a None type binding!
        if bindings is None:
            self._cursor.execute(sql)
        else:
            # pyodbc only supports `qmark` sql params!
            query = sqlparams.SQLParams("format", "qmark")
            sql, bindings = query.format(sql, bindings)
            self._cursor.execute(sql, *bindings)


class SparkConnectionManager(SQLConnectionManager):
    TYPE = "spark"

    SPARK_CLUSTER_HTTP_PATH = "/sql/protocolv1/o/{organization}/{cluster}"
    SPARK_SQL_ENDPOINT_HTTP_PATH = "/sql/1.0/endpoints/{endpoint}"
    SPARK_CONNECTION_URL = "{host}:{port}" + SPARK_CLUSTER_HTTP_PATH

    @contextmanager
    def exception_handler(self, sql: str) -> Generator[None, None, None]:
        try:
            yield

        except Exception as exc:
            logger.debug("Error while running:\n{}".format(sql))
            logger.debug(exc)
            if len(exc.args) == 0:
                raise

            thrift_resp = exc.args[0]
            if hasattr(thrift_resp, "status"):
                msg = thrift_resp.status.errorMessage
                raise DbtRuntimeError(msg)
            else:
                raise DbtRuntimeError(str(exc))

    def cancel(self, connection: Connection) -> None:
        connection.handle.cancel()

    @classmethod
    def get_response(cls, cursor: Any) -> AdapterResponse:
        # https://github.com/dbt-labs/dbt-spark/issues/142
        message = "OK"
        return AdapterResponse(_message=message)

    # No transactions on Spark....
    def add_begin_query(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("NotImplemented: add_begin_query")

    def add_commit_query(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("NotImplemented: add_commit_query")

    def commit(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("NotImplemented: commit")

    def rollback(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("NotImplemented: rollback")

    @classmethod
    def validate_creds(cls, creds: Any, required: Iterable[str]) -> None:
        method = creds.method

        for key in required:
            if not hasattr(creds, key):
                raise DbtConfigError(
                    "The config '{}' is required when using the {} method"
                    " to connect to Spark".format(key, method)
                )

    @classmethod
    def open(cls, connection: Connection) -> Connection:
        if connection.state == ConnectionState.OPEN:
            logger.debug("Connection is already open, skipping open.")
            return connection

        creds = connection.credentials
        exc = None
        handle: SparkConnectionWrapper

        for i in range(1 + creds.connect_retries):
            try:
                if creds.method == SparkConnectionMethod.HTTP:
                    cls.validate_creds(creds, ["token", "host", "port", "cluster", "organization"])

                    # Prepend https:// if it is missing
                    host = creds.host
                    if not host.startswith("https://"):
                        host = "https://" + creds.host

                    conn_url = cls.SPARK_CONNECTION_URL.format(
                        host=host,
                        port=creds.port,
                        organization=creds.organization,
                        cluster=creds.cluster,
                    )

                    logger.debug("connection url: {}".format(conn_url))

                    transport = THttpClient.THttpClient(conn_url)

                    raw_token = "token:{}".format(creds.token).encode()
                    token = base64.standard_b64encode(raw_token).decode()
                    transport.setCustomHeaders({"Authorization": "Basic {}".format(token)})

                    conn = hive.connect(
                        thrift_transport=transport,
                        configuration=creds.server_side_parameters,
                    )
                    handle = PyhiveConnectionWrapper(conn)
                elif creds.method == SparkConnectionMethod.THRIFT:
                    if str(creds.host).startswith("s3://"):
                        creds.host = fetch_host_from_s3(creds.host).strip()
                        logger.info(f"fetch host is {creds.host}")

                    cls.validate_creds(creds, ["host", "port", "user", "schema"])

                    if creds.use_ssl:
                        transport = build_ssl_transport(
                            host=creds.host,
                            port=creds.port,
                            username=creds.user,
                            auth=creds.auth,
                            kerberos_service_name=creds.kerberos_service_name,
                            password=creds.password,
                        )
                        conn = hive.connect(
                            thrift_transport=transport,
                            configuration=creds.server_side_parameters,
                        )
                    else:
                        conn = hive.connect(
                            host=creds.host,
                            port=creds.port,
                            username=creds.user,
                            auth=creds.auth,
                            kerberos_service_name=creds.kerberos_service_name,
                            password=creds.password,
                            configuration=creds.server_side_parameters,
                        )  # noqa
                    handle = PyhiveConnectionWrapper(conn)
                elif creds.method == SparkConnectionMethod.ODBC:
                    if creds.cluster is not None:
                        required_fields = [
                            "driver",
                            "host",
                            "port",
                            "token",
                            "organization",
                            "cluster",
                        ]
                        http_path = cls.SPARK_CLUSTER_HTTP_PATH.format(
                            organization=creds.organization, cluster=creds.cluster
                        )
                    elif creds.endpoint is not None:
                        required_fields = ["driver", "host", "port", "token", "endpoint"]
                        http_path = cls.SPARK_SQL_ENDPOINT_HTTP_PATH.format(
                            endpoint=creds.endpoint
                        )
                    else:
                        raise DbtConfigError(
                            "Either `cluster` or `endpoint` must set when"
                            " using the odbc method to connect to Spark"
                        )

                    cls.validate_creds(creds, required_fields)

                    dbt_spark_version = __version__.version
                    user_agent_entry = (
                        f"dbt-labs-dbt-spark/{dbt_spark_version} (Databricks)"  # noqa
                    )

                    # http://simba.wpengine.com/products/Spark/doc/ODBC_InstallGuide/unix/content/odbc/hi/configuring/serverside.htm
                    ssp = {f"SSP_{k}": f"{{{v}}}" for k, v in creds.server_side_parameters.items()}

                    # https://www.simba.com/products/Spark/doc/v2/ODBC_InstallGuide/unix/content/odbc/options/driver.htm
                    connection_str = _build_odbc_connnection_string(
                        DRIVER=creds.driver,
                        HOST=creds.host,
                        PORT=creds.port,
                        UID="token",
                        PWD=creds.token,
                        HTTPPath=http_path,
                        AuthMech=3,
                        SparkServerType=3,
                        ThriftTransport=2,
                        SSL=1,
                        UserAgentEntry=user_agent_entry,
                        LCaseSspKeyName=0 if ssp else 1,
                        **ssp,
                    )

                    conn = pyodbc.connect(connection_str, autocommit=True)
                    handle = PyodbcConnectionWrapper(conn)
                elif creds.method == SparkConnectionMethod.SESSION:
                    from .session import (  # noqa: F401
                        Connection,
                        SessionConnectionWrapper,
                    )

                    handle = SessionConnectionWrapper(
                        Connection(server_side_parameters=creds.server_side_parameters)
                    )
                elif creds.method == SparkConnectionMethod.SERVERLESS_SPARK:
                    handle = ServerlessSparkConnectionWrapper(connection)
                else:
                    raise DbtConfigError(f"invalid credential method: {creds.method}")
                break
            except Exception as e:
                logger.error(f"ERROR: {e}")
                exc = e
                if isinstance(e, EOFError):
                    # The user almost certainly has invalid credentials.
                    # Perhaps a token expired, or something
                    msg = "Failed to connect"
                    if creds.token is not None:
                        msg += ", is your token valid?"
                    raise FailedToConnectError(msg) from e
                retryable_message = _is_retryable_error(e)
                if retryable_message and creds.connect_retries > 0:
                    msg = (
                        f"Warning: {retryable_message}\n\tRetrying in "
                        f"{creds.connect_timeout} seconds "
                        f"({i} of {creds.connect_retries})"
                    )
                    logger.warning(msg)
                    time.sleep(creds.connect_timeout)
                elif creds.retry_all and creds.connect_retries > 0:
                    msg = (
                        f"Warning: {getattr(exc, 'message', 'No message')}, "
                        f"retrying due to 'retry_all' configuration "
                        f"set to true.\n\tRetrying in "
                        f"{creds.connect_timeout} seconds "
                        f"({i} of {creds.connect_retries})"
                    )
                    logger.warning(msg)
                    time.sleep(creds.connect_timeout)
                else:
                    raise FailedToConnectError("failed to connect") from e
        else:
            raise exc  # type: ignore

        connection.handle = handle
        connection.state = ConnectionState.OPEN
        return connection

    @classmethod
    def data_type_code_to_name(cls, type_code: Union[type, str]) -> str:  # type: ignore
        """
        :param Union[type, str] type_code: The sql to execute.
            * type_code is a python type (!) in pyodbc https://github.com/mkleehammer/pyodbc/wiki/Cursor#description, and a string for other spark runtimes.
            * ignoring the type annotation on the signature for this adapter instead of updating the base class because this feels like a really special case.
        :return: stringified the cursor type_code
        :rtype: str
        """
        if isinstance(type_code, str):
            return type_code
        return type_code.__name__.upper()

###############################################################
def parse_s3_uri(full_path) :
    s3_prefix = 's3://'
    if not full_path.startswith(s3_prefix):
        raise ValueError('Invalid S3 URL')

    bucket = urlparse(full_path).netloc
    path = full_path.split(bucket)[1][1:]
    return bucket, path

def fetch_host_from_s3(s3_path):
    client = boto3.client('s3')
    bucket, path = parse_s3_uri(s3_path)
    # 获取s3文件
    obj = client.get_object(
        Bucket=bucket,
        Key=path
    )

    # 返回s3文件文本
    return obj.get('Body').read().decode('utf-8')
###############################################################

def build_ssl_transport(
        host: str,
        port: int,
        username: str,
        auth: str,
        kerberos_service_name: str,
        password: Optional[str] = None,
) -> "thrift_sasl.TSaslClientTransport":
    transport = None
    if port is None:
        port = 10000
    if auth is None:
        auth = "NONE"
    socket = TSSLSocket(host, port, cert_reqs=ssl.CERT_NONE)
    if auth == "NOSASL":
        # NOSASL corresponds to hive.server2.authentication=NOSASL
        # in hive-site.xml
        transport = thrift.transport.TTransport.TBufferedTransport(socket)
    elif auth in ("LDAP", "KERBEROS", "NONE", "CUSTOM"):
        # Defer import so package dependency is optional
        if auth == "KERBEROS":
            # KERBEROS mode in hive.server2.authentication is GSSAPI
            # in sasl library
            sasl_auth = "GSSAPI"
        else:
            sasl_auth = "PLAIN"
            if password is None:
                # Password doesn't matter in NONE mode, just needs
                # to be nonempty.
                password = "x"

        def sasl_factory() -> SASLClient:
            if sasl_auth == "GSSAPI":
                sasl_client = SASLClient(host, kerberos_service_name, mechanism=sasl_auth)
            elif sasl_auth == "PLAIN":
                sasl_client = SASLClient(
                    host, mechanism=sasl_auth, username=username, password=password
                )
            else:
                raise AssertionError
            return sasl_client

        transport = thrift_sasl.TSaslClientTransport(sasl_factory, sasl_auth, socket)
    return transport


def _is_retryable_error(exc: Exception) -> str:
    message = str(exc).lower()
    if "pending" in message or "temporarily_unavailable" in message:
        return str(exc)
    else:
        return ""


class ServerlessSparkConnectionWrapper(SparkConnectionWrapper):
    """Wrap a Spark connection in a way that no-ops transactions"""

    # https://forums.databricks.com/questions/2157/in-apache-spark-sql-can-we-roll-back-the-transacti.html  # noqa

    handle: "pyodbc.Connection"
    _cursor: "Optional[pyodbc.Cursor]"

    from enum import Enum

    class AppState(Enum):
        """
        EMR Serverless Spark Job Run States
        """

        SUBMITTED = "Submitted"
        PENDING = "Pending"
        RUNNING = "Running"
        SUCCESS = "Success"
        FAILED = "Failed"
        CANCELLING = "Cancelling"
        CANCELLED = "Cancelled"
        CANCEL_FAILED = "CancelFailed"

    def __init__(self, connection) -> None:
        self.connection = connection
        self._cursor = None

        creds = connection.credentials
        self._workspace_id = creds.workspace_id
        self._region = creds.region
        self.parse_result = None

        import os

        if creds.ak is None or creds.sk is None:
            ak = os.environ["AK"]
            sk = os.environ["SK"]
        else:
            ak = creds.ak
            sk = creds.sk

        self._client = Client(
            Config(
                access_key_id=ak,
                access_key_secret=sk,
                endpoint=f"emr-serverless-spark.{creds.region}.aliyuncs.com",
            )
        )

        self._current_job_run_id = None

        try:
            thrift_conn = hive.connect(
                host=creds.host,
                port="443",
                username=creds.user,
                auth=None,
                password=creds.password,
                scheme="https",
                configuration=creds.server_side_parameters,
            )  # noqa
            # thrift_conn = hive.connect(
            #     host=creds.host,
            #     port=creds.port,
            #     username=creds.user,
            #     auth=creds.auth,
            #     kerberos_service_name=creds.kerberos_service_name,
            #     password=creds.password,
            #     configuration=creds.server_side_parameters,
            # )  # noqa
        except Exception as e:
            logger.error(e)
            raise e

        self._interactive = PyhiveConnectionWrapper(thrift_conn)
        self._is_interactive = False

    def cursor(self) -> "ServerlessSparkConnectionWrapper":
        self._interactive._cursor = self._interactive.handle.cursor()
        return self

    def cancel(self) -> None:
        self.release_locks(self.parse_result)
        try:
            self._interactive.cancel()
        except Exception as e:
            pass

        if self._current_job_run_id == None:
            logger.debug("No job running, no need to cancel.")
        else:
            logger.debug("Canceling job run - %s", self._current_job_run_id)
            try:
                self._client.cancel_job_run(
                    self._workspace_id, self._current_job_run_id, CancelJobRunRequest(region_id=self._region)
                )
            except Exception as e:
                raise Exception(f"Errors when canceling job run: {self._current_job_run_id}") from e

    def close(self) -> None:
        # Currently serverless spark sdk client does not support close
        try:
            self.release_locks(self.parse_result)
            self._interactive.close()
        except Exception as e:
            pass

    def rollback(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("NotImplemented: rollback")

    def fetchall(self) -> List["pyodbc.Row"]:
        if self._is_interactive:
            result = self._interactive.fetchall()
        else:
            workspace_id = self.connection.credentials.workspace_id
            region_id = self.connection.credentials.region
            get_job_run_response = self._client.get_job_run(
                workspace_id, self._current_job_run_id, GetJobRunRequest(region_id=region_id)
            )
            time.sleep(10)
            file_name = get_job_run_response.body.job_run.log.driver_std_out
            list_log_content_response = self._client.list_log_contents(workspace_id, ListLogContentsRequest(file_name, 9999, 0, region_id))
            raw_result = list_log_content_response.body.list_log_content.contents[0].line_content
            lines = raw_result.split('\n')
            result = [line.split('\t') for line in lines if line]
            result[0][0] = int(result[0][0])
            result[0][1] = True if result[0][1].lower() == "true" else False
            result[0][2] = True if result[0][2].lower() == "true" else False

        return result

    def execute(self, sql: str, bindings: Optional[List[Any]] = None) -> None:
        if self._use_interactive_runner(sql):
            self._interactive.execute(sql, bindings)
            self._is_interactive = True
            return

        self._is_interactive = False

        credentials = self.connection.credentials

        env = "production"
        tags: List[Tag] = [Tag("environment", env), Tag("workflow", "true")]
        engine_release_version = (
            "esr-2.2.2 (Spark 3.3.1, Scala 2.12, Java Runtime)"
        )

        spark_confs = ""
        for key, value in credentials.server_side_parameters.items():
            spark_confs += f" --conf {key}={value}"
        spark_submit_parameters = f"--class org.apache.spark.sql.hive.thriftserver.SparkSQLCLIDriver {spark_confs}"
        logger.debug("[ss-debugger] spark_submit_parameters - {}", spark_submit_parameters)
        entry_point_args = ["-e", sql]
        job_driver_spark_submit = JobDriverSparkSubmit(
            None, entry_point_args, spark_submit_parameters
        )

        job_driver = JobDriver(job_driver_spark_submit)

        start_job_run_request = StartJobRunRequest(
            region_id=credentials.region,
            resource_queue_id="root_queue",
            code_type="SQL",
            name=self._generate_serverless_spark_job_name(sql),
            release_version=engine_release_version,
            tags=tags,
            job_driver=job_driver,
            fusion=True,
        )

        runtime = util_models.RuntimeOptions()
        headers = {}

        ######################################################
        parse_result = self.assert_source_table_succeed(sql, True)
        self.catch_locks(parse_result)
        ######################################################

        try:
            job_run_id = self._client.start_job_run_with_options(
                credentials.workspace_id, start_job_run_request, headers, runtime
            ).body.job_run_id

            logger.debug("job_run_id - {}", job_run_id)
            self._current_job_run_id = job_run_id

            state = self._client.get_job_run(
                credentials.workspace_id, job_run_id, GetJobRunRequest(region_id=credentials.region)
            ).body.job_run.state

            while ServerlessSparkConnectionWrapper.AppState(state) not in {
                ServerlessSparkConnectionWrapper.AppState.SUCCESS,
                ServerlessSparkConnectionWrapper.AppState.FAILED,
                ServerlessSparkConnectionWrapper.AppState.CANCELLED,
                ServerlessSparkConnectionWrapper.AppState.CANCEL_FAILED}:
                time.sleep(10)
                logger.debug("Poll status: {}, sleeping".format(state))

                state = self._client.get_job_run(
                    credentials.workspace_id, job_run_id, GetJobRunRequest(region_id=credentials.region)
                ).body.job_run.state

            if ServerlessSparkConnectionWrapper.AppState(state) in (
                    ServerlessSparkConnectionWrapper.AppState.CANCELLED,
                    ServerlessSparkConnectionWrapper.AppState.CANCEL_FAILED):
                self.release_locks(parse_result)
                raise DbtDatabaseError("Query failed with status: {}".format(state))

            if ServerlessSparkConnectionWrapper.AppState(state) == ServerlessSparkConnectionWrapper.AppState.FAILED:
                self.release_locks(parse_result)
                raise DbtDatabaseError(self._client.get_job_run(
                    credentials.workspace_id, job_run_id, GetJobRunRequest(region_id=credentials.region)
                ).body.job_run.state_change_reason.message + "\n" + sql)
            else:
                logger.debug("Job run finished with state - {}", state)

            self.release_locks(parse_result)
        except Exception as e:
            self.release_locks(parse_result)
            raise DbtDatabaseError(str(e))
        return

    @classmethod
    def _fix_binding(cls, value: Any) -> Union[float, str]:
        """Convert complex datatypes to primitives that can be loaded by
        the Spark driver"""
        if isinstance(value, NUMBERS):
            return float(value)
        elif isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        else:
            return value

    @property
    def description(
            self,
    ) -> Sequence[
        Tuple[str, Any, Optional[int], Optional[int], Optional[int], Optional[int], bool]
    ]:
        try:
            if self._is_interactive:
                result = self._interactive._cursor.description
            else:
                result = [('failures', 'BIGINT_TYPE', None, None, None, None, True),
                      ('should_warn', 'BOOLEAN_TYPE', None, None, None, None, True),
                      ('should_error', 'BOOLEAN_TYPE', None, None, None, None, True)]
            return result
        except Exception as e:
            return []

    def _generate_serverless_spark_job_name(self, sql):
        import re
        import json
        name = "dbt-job-default-name"
        try:
            # Regular expression to find the text between '/*' and '*/'
            match = re.search(r'/\*(.*?)\*/', sql, re.DOTALL)
            comment = None
            if match:
                comment = match.group(1).strip()

            comment_dict = json.loads(comment)
            if "connection_name" in comment_dict:
                name = comment_dict["connection_name"]
            elif "node_id" in comment_dict:
                name = comment_dict["node_id"]
            else:
                pass

        except Exception as e:
            logger.debug("Failed to generate spark job name!", e)

        logger.debug("Generated spark job name - {}", name)

        return name

    def _use_interactive_runner(self, sql):
        interactive_keywords = ["drop table if exists ",
                                "alter table ",
                                "show table extended ",
                                "describe extended ",
                                "create schema if not exists ",
                                "show databases",
                                "create or replace view ",
                                "clear cache"]
        return True or any(keyword in sql.lower() for keyword in interactive_keywords) or self._is_just_dbt_tmp(sql)

    def _is_just_dbt_tmp(self, sql):
        # "__dbt_tmp" 1 次以上，则代表为 create or replace tempoary view + insert 拼接作业；
        return sql.count('__dbt_tmp') == 1

