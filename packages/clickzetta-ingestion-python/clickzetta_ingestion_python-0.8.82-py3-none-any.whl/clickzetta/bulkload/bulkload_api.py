import json
from logging import getLogger

import requests
from google.protobuf.json_format import MessageToJson, ParseDict

from clickzetta.bulkload._proto import ingestion_pb2
from clickzetta.bulkload.bulkload_enums import (
    BulkLoadCommitMode,
    BulkLoadCommitOptions,
    BulkLoadConfig,
    BulkLoadMetaData,
    BulkLoadOperation,
    BulkLoadOptions,
)
from clickzetta.bulkload.bulkload_stream import BulkLoadStream
from clickzetta.connector.v0.client import Client

HEADERS = {"Content-Type": "application/json"}

_log = getLogger(__name__)

def _gate_way_call(client: Client, request, method):
    path = "/igs/gatewayEndpoint"
    gate_way_request = ingestion_pb2.GatewayRequest()
    gate_way_request.methodEnumValue = method
    gate_way_request.message = MessageToJson(request)

    HEADERS["instanceName"] = client.instance
    HEADERS["X-ClickZetta-Token"] = client.token
    result_dict = {}
    try:
        api_response = requests.post(
            client.service + path,
            data=MessageToJson(gate_way_request),
            headers=HEADERS,
        )
        api_response.encoding = "utf-8"
        result = api_response.text
        try:
            result_dict = json.loads(result)
        except Exception:
            _log.error(f"gate_way_call error:{result}")
            raise Exception(f"gate_way_call error:{result}")
        if api_response.status_code != 200:
            raise requests.exceptions.RequestException(
                "gate_way_call return failed code.Error message:"
                + result_dict["message"]
            )
        result_status = ParseDict(
            result_dict["status"], ingestion_pb2.GateWayResponseStatus
        )
        if result_status.code == ingestion_pb2.Code.SUCCESS:
            message_json = json.loads(result_dict["message"])
            internal_result_status = message_json["status"]
            if internal_result_status["code"] == "SUCCESS":
                return json.loads(result_dict["message"])
            else:
                raise requests.exceptions.RequestException(
                    "gate_way_call return failed code.Error message:"
                    + internal_result_status["error_message"]
                )
        else:
            raise requests.exceptions.RequestException(
                "gate_way_call return failed code.Error message:"
                + result_status.message
            )

    except requests.exceptions.RequestException as request_exception:
        _log.error("gate_way_request error:{} result dict: {}".format(request_exception, result_dict))
        raise requests.exceptions.RequestException(
            "gate_way_request error:{} result dict: {}".format(request_exception, result_dict)
        )
    except Exception as e:
        _log.error("gate_way_request error:{} result dict: {}".format(e, result_dict))
        raise requests.exceptions.RequestException(
            "gate_way_request error:{} result dict: {}".format(e, result_dict)
        )


def create_bulkload_stream(client: Client, **kwargs):
    schema = kwargs.get("schema", client.schema)
    table = kwargs.get("table")
    if schema is None:
        schema = client.schema
    if schema is None:
        raise ValueError(f"No schema specified")
    if table is None:
        raise ValueError(f"No table specified")

    operation = kwargs.get("operation", BulkLoadOperation.APPEND)
    workspace = kwargs.get("workspace", client.workspace)
    vcluster = kwargs.get("vcluster", client.vcluster)
    partition_spec = kwargs.get("partition_spec")
    record_keys = kwargs.get("record_keys")
    prefer_internal_endpoint = kwargs.get("prefer_internal_endpoint", False)

    bulkload_meta_data = client.create_bulkload_stream(
        schema,
        table,
        BulkLoadOptions(
            operation, partition_spec, record_keys, prefer_internal_endpoint
        ),
    )
    return BulkLoadStream(
        bulkload_meta_data, client, BulkLoadCommitOptions(workspace, vcluster)
    )


def get_bulkload_stream(
    client: Client, stream_id: str, schema: str = None, table: str = None
):
    bulkload_meta_data = client.get_bulkload_stream(schema, table, stream_id)
    return BulkLoadStream(
        bulkload_meta_data,
        client,
        BulkLoadCommitOptions(client.workspace, client.vcluster),
    )


def create_bulkload_stream_metadata(
    client: Client, schema_name: str, table_name: str, options
) -> BulkLoadMetaData:
    create_bulk_load_request = ingestion_pb2.CreateBulkLoadStreamRequest()
    account = ingestion_pb2.Account()
    user_ident = ingestion_pb2.UserIdentifier()
    user_ident.instance_id = client.instance_id
    user_ident.workspace = client.workspace
    user_ident.user_name = client.username
    account.user_ident.CopyFrom(user_ident)
    account.token = client.token
    create_bulk_load_request.account.CopyFrom(account)
    table_identifier = ingestion_pb2.TableIdentifier()
    table_identifier.instance_id = client.instance_id
    table_identifier.workspace = client.workspace
    table_identifier.schema_name = schema_name
    table_identifier.table_name = table_name
    create_bulk_load_request.identifier.CopyFrom(table_identifier)
    if options.operation == BulkLoadOperation.APPEND:
        create_bulk_load_request.operation = (
            ingestion_pb2.BulkLoadStreamOperation.BL_APPEND
        )
    elif options.operation == BulkLoadOperation.UPSERT:
        create_bulk_load_request.operation = (
            ingestion_pb2.BulkLoadStreamOperation.BL_UPSERT
        )
    elif options.operation == BulkLoadOperation.OVERWRITE:
        create_bulk_load_request.operation = (
            ingestion_pb2.BulkLoadStreamOperation.BL_OVERWRITE
        )
    if options.partition_specs is not None:
        create_bulk_load_request.partition_spec = options.partition_specs
    if options.record_keys is not None:
        keys = []
        for key in options.record_keys:
            keys.append(key)
        create_bulk_load_request.record_keys.extend(keys)
    create_bulk_load_request.prefer_internal_endpoint = options.prefer_internal_endpoint
    response = _gate_way_call(
        client,
        create_bulk_load_request,
        ingestion_pb2.MethodEnum.CREATE_BULK_LOAD_STREAM_V2,
    )
    response_pb = ParseDict(
        response,
        ingestion_pb2.CreateBulkLoadStreamResponse(),
        ignore_unknown_fields=True,
    )
    client.instance_id = response_pb.info.identifier.instance_id
    return BulkLoadMetaData(response_pb.info.identifier.instance_id, response_pb.info)


def commit_bulkload_stream(
    client: Client,
    instance_id: int,
    workspace: str,
    schema_name: str,
    table_name: str,
    stream_id: str,
    execute_workspace: str,
    execute_vc: str,
    commit_mode,
):

    commit_bulkload_request = ingestion_pb2.CommitBulkLoadStreamRequest()
    account = ingestion_pb2.Account()
    user_ident = ingestion_pb2.UserIdentifier()
    user_ident.instance_id = instance_id
    user_ident.workspace = workspace
    user_ident.user_name = client.username
    account.user_ident.CopyFrom(user_ident)
    # The account token needs to be passed as an empty value. If need to pass the authentication token,
    # we cannot use `client.token` login token
    account.token = ""
    commit_bulkload_request.account.CopyFrom(account)
    table_identifier = ingestion_pb2.TableIdentifier()
    table_identifier.instance_id = instance_id
    table_identifier.workspace = workspace
    table_identifier.schema_name = schema_name
    table_identifier.table_name = table_name
    commit_bulkload_request.identifier.CopyFrom(table_identifier)
    commit_bulkload_request.stream_id = stream_id
    commit_bulkload_request.execute_workspace = execute_workspace
    commit_bulkload_request.execute_vc_name = execute_vc
    if commit_mode == BulkLoadCommitMode.COMMIT_STREAM:
        commit_bulkload_request.commit_mode = (
            ingestion_pb2.CommitBulkLoadStreamRequest.CommitMode.COMMIT_STREAM
        )
    elif commit_mode == BulkLoadCommitMode.ABORT_STREAM:
        commit_bulkload_request.commit_mode = (
            ingestion_pb2.CommitBulkLoadStreamRequest.CommitMode.ABORT_STREAM
        )

    response = _gate_way_call(
        client,
        commit_bulkload_request,
        ingestion_pb2.MethodEnum.COMMIT_BULK_LOAD_STREAM_V2,
    )
    response_pb = ParseDict(
        response,
        ingestion_pb2.CommitBulkLoadStreamResponse(),
        ignore_unknown_fields=True,
    )
    bulkload_meta_data = BulkLoadMetaData(client.instance_id, response_pb.info)
    return bulkload_meta_data


def get_bulkload_stream_metadata(
    client: Client, schema_name: str, table_name: str, stream_id: str
) -> BulkLoadMetaData:
    get_bulkload_stream_request = ingestion_pb2.GetBulkLoadStreamRequest()
    account = ingestion_pb2.Account()
    user_ident = ingestion_pb2.UserIdentifier()
    user_ident.instance_id = client.instance_id
    user_ident.workspace = client.workspace
    user_ident.user_name = client.username
    account.user_ident.CopyFrom(user_ident)
    account.token = client.token
    get_bulkload_stream_request.account.CopyFrom(account)
    table_identifier = ingestion_pb2.TableIdentifier()
    table_identifier.instance_id = client.instance_id
    table_identifier.workspace = client.workspace
    table_identifier.schema_name = schema_name
    table_identifier.table_name = table_name
    get_bulkload_stream_request.identifier.CopyFrom(table_identifier)
    get_bulkload_stream_request.stream_id = stream_id
    get_bulkload_stream_request.need_table_meta = True
    response = _gate_way_call(
        client,
        get_bulkload_stream_request,
        ingestion_pb2.MethodEnum.GET_BULK_LOAD_STREAM_V2,
    )
    response_pb = ParseDict(
        response,
        ingestion_pb2.GetBulkLoadStreamResponse(),
        ignore_unknown_fields=True,
    )
    bulkload_meta_data = BulkLoadMetaData(client.instance_id, response_pb.info)
    return bulkload_meta_data


def open_bulkload_stream_writer(
    client: Client,
    instance_id: int,
    workspace: str,
    schema_name: str,
    table_name: str,
    stream_id: str,
    partition_id: int,
):
    open_bulkload_stream_request = ingestion_pb2.OpenBulkLoadStreamWriterRequest()
    account = ingestion_pb2.Account()
    user_ident = ingestion_pb2.UserIdentifier()
    user_ident.instance_id = instance_id
    user_ident.workspace = workspace
    user_ident.user_name = client.username
    account.user_ident.CopyFrom(user_ident)
    account.token = client.token
    open_bulkload_stream_request.account.CopyFrom(account)
    table_identifier = ingestion_pb2.TableIdentifier()
    table_identifier.instance_id = instance_id
    table_identifier.workspace = workspace
    table_identifier.schema_name = schema_name
    table_identifier.table_name = table_name
    open_bulkload_stream_request.identifier.CopyFrom(table_identifier)
    open_bulkload_stream_request.stream_id = stream_id
    open_bulkload_stream_request.partition_id = partition_id
    response = _gate_way_call(
        client,
        open_bulkload_stream_request,
        ingestion_pb2.MethodEnum.OPEN_BULK_LOAD_STREAM_WRITER_V2,
    )
    response_pb = ParseDict(
        response,
        ingestion_pb2.OpenBulkLoadStreamWriterResponse(),
        ignore_unknown_fields=True,
    )
    bulkload_config = response_pb.config
    return BulkLoadConfig(bulkload_config)


def finish_bulkload_stream_writer(
    client: Client,
    instance_id: int,
    workspace: str,
    schema_name: str,
    table_name: str,
    stream_id: str,
    partition_id: int,
    written_files: list,
    written_lengths: list,
):

    finish_bulkload_stream_request = ingestion_pb2.FinishBulkLoadStreamWriterRequest()
    account = ingestion_pb2.Account()
    user_ident = ingestion_pb2.UserIdentifier()
    user_ident.instance_id = instance_id
    user_ident.workspace = workspace
    user_ident.user_name = client.username
    account.user_ident.CopyFrom(user_ident)
    account.token = client.token
    finish_bulkload_stream_request.account.CopyFrom(account)
    table_identifier = ingestion_pb2.TableIdentifier()
    table_identifier.instance_id = instance_id
    table_identifier.workspace = workspace
    table_identifier.schema_name = schema_name
    table_identifier.table_name = table_name
    finish_bulkload_stream_request.identifier.CopyFrom(table_identifier)
    finish_bulkload_stream_request.stream_id = stream_id
    finish_bulkload_stream_request.partition_id = partition_id
    finish_bulkload_stream_request.written_files.extend(written_files)
    finish_bulkload_stream_request.written_lengths.extend(written_lengths)
    response = _gate_way_call(
        client,
        finish_bulkload_stream_request,
        ingestion_pb2.MethodEnum.FINISH_BULK_LOAD_STREAM_WRITER_V2,
    )
    response_pb = ParseDict(
        response,
        ingestion_pb2.FinishBulkLoadStreamWriterResponse(),
        ignore_unknown_fields=True,
    )
    return response_pb.status
