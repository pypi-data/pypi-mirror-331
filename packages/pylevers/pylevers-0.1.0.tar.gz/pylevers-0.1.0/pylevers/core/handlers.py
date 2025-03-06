import time

import grpc

from google.protobuf.json_format import MessageToDict
from .types import LeversException
from .types import SearchResults
from .types import MutableResult
from .types import GetResult
from .types import ListResult
from .types import DescribeResult
from .types import StatsResult
from .types import Status
from .types import ConnectResult
from .types import ClientInfo

from .types import common_pb2
from .types import levers_pb2
from .types import levers_pb2_grpc
from .. import __version__


class BaseHandler:
    @staticmethod
    def _parse_response(pb_or_txt):
        pb = pb_or_txt
        if isinstance(pb, common_pb2.Status):
            return Status.from_pb(pb)
        status = Status(pb.status.error_code, pb.status.reason)
        if not status.ok():
            return status, None
        rsp = MessageToDict(pb, always_print_fields_with_no_presence=True)
        return status, rsp

    @staticmethod
    def _parse_status(pb_status):
        return Status.from_pb(pb_status)


class GrpcHandler(BaseHandler):
    def __init__(self, host, port):
        # hostname
        self._host = host
        # port
        self._port = port
        self._channel = None
        self.new_channel()

    def new_channel(self):
        spec = f'{self._host}:{self._port}'
        if self._channel:
            self.close()
        self._channel = grpc.insecure_channel(spec)
        self._stub = levers_pb2_grpc.LeversServiceStub(self._channel)

    def connect(self):
        client_info = ClientInfo(
            sdk_type='python',
            sdk_version=__version__,
            local_time=str(time.time()),
            user='admin',
            host=self._host)
        req = levers_pb2.ConnectRequest()
        req.client_info.CopyFrom(client_info.to_pb())
        pb_rsp = self._stub.Connect(req)
        rsp = ConnectResult.from_pb(pb_rsp)
        return rsp.status, rsp.results

    def create_collection(self, collection_schema):
        req = levers_pb2.CreateCollectionRequest()
        pb_collection_schema = collection_schema.to_pb()
        req.schema.CopyFrom(pb_collection_schema)
        rsp = self._stub.CreateCollection(req)
        return Status.from_pb(rsp)

    def drop_collection(self, collection_name):
        req = levers_pb2.DropCollectionRequest()
        req.collection_name = collection_name
        rsp = self._stub.DropCollection(req)
        return Status.from_pb(rsp)

    def list_collections(self):
        req = levers_pb2.ListCollectionsRequest()
        pb_rsp = self._stub.ListCollections(req)
        rsp = ListResult.from_pb(pb_rsp)
        return rsp.status, rsp.results

    def describe_collection(self, collection_name):
        req = levers_pb2.DescribeCollectionRequest()
        req.collection_name = collection_name
        pb_rsp = self._stub.DescribeCollection(req)
        rsp = DescribeResult.from_pb(pb_rsp)
        return rsp.status, rsp.results

    def stats_collection(self, collection_name):
        req = levers_pb2.StatsCollectionRequest()
        req.collection_name = collection_name
        pb_rsp = self._stub.StatsCollection(req)
        rsp = StatsResult.from_pb(pb_rsp)
        return rsp.status, rsp.results

    def insert(self, collection_name, entity_metas, entity_datas):
        if collection_name is None or len(collection_name) == 0:
            raise LeversException("collection name is not valid")

        if len(entity_metas) == 0:
            raise LeversException("no entity meta")

        if len(entity_datas) > 1000:
            raise LeversException("insert entity data size is too large")

        for index, entity_data in enumerate(entity_datas):
            try:
                entity_data._valid_check()
            except LeversException:
                raise LeversException("entity data " + str(index) + " not valid")

        pb_insert_request = levers_pb2.InsertRequest()
        pb_insert_request.collection_name = collection_name
        pb_insert_request.entity_metas.extend(
            entity_meta.to_pb() for entity_meta in entity_metas)
        pb_insert_request.entity_datas.extend(
            entity_data.to_pb(entity_metas) for entity_data in entity_datas)
        pb_rsp = self._stub.Insert(pb_insert_request)
        rsp = MutableResult.from_pb(pb_rsp)
        return rsp.status, rsp

    def update(self, collection_name, entity_metas, entity_datas):
        if collection_name is None or len(collection_name) == 0:
            raise LeversException("collection name is not valid")

        if len(entity_metas) == 0:
            raise LeversException("no entity meta")

        for index, entity_data in enumerate(entity_datas):
            try:
                entity_data._valid_check()
            except LeversException:
                raise LeversException("entity data " + str(index) + " not valid")

        pb_update_request = levers_pb2.UpdateRequest()
        pb_update_request.collection_name = collection_name
        pb_update_request.entity_metas.extend(
            entity_meta.to_pb() for entity_meta in entity_metas)
        pb_update_request.entity_datas.extend(
            entity_data.to_pb(entity_metas) for entity_data in entity_datas)
        pb_rsp = self._stub.Update(pb_update_request)
        rsp = MutableResult.from_pb(pb_rsp)
        return rsp.status, rsp

    def delete(self, collection_name, pks):
        if collection_name is None or len(collection_name) == 0:
            raise LeversException("collection name is not valid")

        if len(pks) == 0:
            raise LeversException("no entity pk")

        for index, pk in enumerate(pks):
            if not isinstance(pk, int):
                raise LeversException("entity pk " + str(index) + " not valid")

        pb_delete_request = levers_pb2.DeleteRequest()
        pb_delete_request.collection_name = collection_name
        pb_delete_request.pks.extend(pks)
        pb_rsp = self._stub.Delete(pb_delete_request)
        rsp = MutableResult.from_pb(pb_rsp)
        return rsp.status, rsp

    def search(self, collection_name, knn_param, topk, filter, output_fields, extra_params):
        if collection_name is None or len(collection_name) == 0:
            raise LeversException("collection name is not valid")

        pb_search_request = levers_pb2.SearchRequest()
        pb_search_request.collection_name = collection_name
        if knn_param is not None:
            pb_search_request.knn_param.CopyFrom(knn_param.to_pb())
        pb_search_request.topk = topk
        if filter:
            pb_search_request.filter = filter
        pb_search_request.output_fields.extend(output_fields)
        if extra_params is not None:
            pb_search_request.extra_params.update(extra_params)

        pb_rsp = self._stub.Search(pb_search_request)
        rsp = SearchResults.from_pb(pb_rsp)
        return rsp.status, rsp.results

    def get(self, collection_name, pk, output_fields, extra_params):
        if collection_name is None or len(collection_name) == 0:
            raise LeversException("collection name is not valid")

        pb_get_request = levers_pb2.GetRequest()
        pb_get_request.collection_name = collection_name
        pb_get_request.pk = pk
        pb_get_request.output_fields.extend(output_fields)
        if extra_params is not None:
            pb_get_request.extra_params.update(extra_params)

        pb_rsp = self._stub.Get(pb_get_request)
        rsp = GetResult.from_pb(pb_rsp)
        return rsp.status, rsp.entity_data

    def close(self):
        self._channel.close()
