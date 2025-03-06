import abc
import grpc
from .handlers import GrpcHandler

import time
from functools import wraps

from pylevers.core import types
from .types import common_pb2

def _retry_logic(func, self, max_retries, base_delay, retries, e):
    """
    Helper function to handle retry logic.
    """
    if max_retries != -1 and retries > max_retries:
        raise e

    print(f"Retrying {func.__name__} due to error: {str(e)} (Attempt {retries})")

    delay_time = base_delay * (2 ** (retries - 1))
    print(f"Waiting for {delay_time} seconds before retrying...")
    time.sleep(delay_time)
    # Recreate the channel to avoid stale connections
    self._handler.new_channel()

def _retry_on_failure(max_retries=-1, base_delay=1):
    """
    Retry decorator for methods that may fail due to network issues.
    If max_retries is set to -1, it will retry indefinitely.
    If max_retries is a positive integer, it will retry up to max_retries times.

    Args:
        max_retries (int): Number of retry attempts. Set to -1 for infinite retries.
        base_delay (int): Base delay in seconds between retries, which will increase exponentially.
                        Defaults to 1 second.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            retries = 0
            while True:
                try:
                    rsp = func(self, *args, **kwargs)
                    status = None
                    if isinstance(rsp, tuple):
                        status = rsp[0]
                    elif isinstance(rsp, types.Status):
                        status = rsp
                    if (status is not None) and ( status.code == common_pb2.ErrorCode.Eagain \
                        or status.code == common_pb2.ErrorCode.Enomem \
                        or status.code == common_pb2.ErrorCode.Ebusy \
                        or status.code == common_pb2.ErrorCode.Eremchg \
                        or status.code == common_pb2.ErrorCode.Etimedout \
                        or status.code == common_pb2.ErrorCode.Ecanceled \
                        or status.code == common_pb2.ErrorCode.Econnaborted \
                        or status.code == common_pb2.ErrorCode.Econnreset \
                        or status.code == common_pb2.ErrorCode.Enotconn \
                        or status.code == common_pb2.ErrorCode.Eshutdown):
                        # print("wzbdebug: ", status.code, status.reason)
                        retries += 1
                        _retry_logic(func, self, max_retries, base_delay, retries, Exception(f"Error code: {status.code}"))
                    return rsp
                except grpc.RpcError as e:
                    retries += 1
                    _retry_logic(func, self, max_retries, base_delay, retries, e)
                except Exception as e:
                    print(type(e))
                    print(f"Encountered non-retryable error: {str(e)}")
                    raise e
        return wrapper
    return decorator


class BaseClient(abc.ABC):

    """
    BaseClient.
    """

    @abc.abstractmethod
    def __init__(self, handler):
        self._handler = handler

    def connect(self):
        """
        Connect to Levers.
        Returns:
        tuple: 2-element tuple containing
          * :class:`Status`: status
          * :class:`ServerInfo`: serverinfo
        """
        return self._handler.connect()

    @_retry_on_failure(max_retries=7)
    def create_collection(self, collection_schema):
        """
        Create collection.

        Args:
            collection_schema (CollectionSchema): create collection schema.

        Returns:
            * :class:`Status`: status
        """
        return self._handler.create_collection(collection_schema)

    @_retry_on_failure(max_retries=7)
    def describe_collection(self, collection_name):
        """
        Describe collection.

        Args:
            collection_names (list):  collection names

        Returns:
            tuple: 2-element tuple containing
              * :class:`Status`: status
              * :list[class: `CollectionSchema`]: collection info
        """
        return self._handler.describe_collection(collection_name)

    @_retry_on_failure(max_retries=7)
    def drop_collection(self, collection_name):
        """
        Drop collection.

        Args:
            collection_name (str): collection name

        Returns:
            * :class:`Status`: status
        """
        return self._handler.drop_collection(collection_name)

    @_retry_on_failure(max_retries=7)
    def list_collections(self):
        """
        List all collections.

        Returns:
            tuple: 2-element tuple containing
              * :class:`Status`: status
              * list[str]: name list
        """
        return self._handler.list_collections()

    @_retry_on_failure(max_retries=7)
    def stats_collection(self, collection_name):
        """
        Get collection statistics.

        Args:
            collection_names (list): collection names

        Returns:
            tuple: 2-element tuple containing
              * :class:`Status`: status
              * list[class:`CollectionStats`]: collection stats list
        """
        return self._handler.stats_collection(collection_name)

    @_retry_on_failure(max_retries=7)
    def insert(self, collection_name, entity_metas, entity_datas):
        """
        Insert Entities.

        Args:
            collection_name (str): collection name
            entity_datas (List[EntityData]): list of entity data to be inserted

        Returns:
            tuple: 2-element tuple containing
              * :class:`Status`: status
              * list[int]: results
        """
        return self._handler.insert(collection_name, entity_metas, entity_datas)

    @_retry_on_failure(max_retries=7)
    def update(self, collection_name, entity_metas, entity_datas):
        """
        Update Entities.

        Args:
            collection_name (str): collection name
            entity_datas (List[EntityData]): list of entity data to be updated

        Returns:
            tuple: 2-element tuple containing
              * :class:`Status`: status
              * list[int]: results
        """
        return self._handler.update(collection_name, entity_metas, entity_datas)

    @_retry_on_failure(max_retries=7)
    def delete(self, collection_name, pks):
        """
        Delete Entities.

        Args:
            collection_name (str): collection name
            pks (List[(str)]): list of entity pks to be deleted

        Returns:
            tuple: 2-element tuple containing
              * :class:`Status`: status
              * list[int]: results
        """
        return self._handler.delete(collection_name, pks)

    @_retry_on_failure(max_retries=7)
    def search(self, collection_name, knn_param=None, topk=0, filter='', output_fields=None, extra_params=None):
        """
        knn search

        Args:
            collection_name (str): collection name
            knn_param (Optional(KnnParam)): params for knn search
            topk(Optional(int)): topk
            filter(Optional(str)): filter expression
            output_fields(Optional(List(str))): list of output field name str
            extra_params(Optional(Dict)): extra params

        Returns:
            tuple: 2-element tuple containing
              * :class:`Status`: status
              * list[SearchResult]: search results
        """
        return self._handler.search(collection_name, knn_param, topk, filter, output_fields, extra_params)

    @_retry_on_failure(max_retries=7)
    def get(self, collection_name, pk, output_fields=None, extra_params=None):
        """
        get entity by pk

        Args:
            collection_name (str): collection name
            pk (int): primary key for entity to get
            output_fields(Optional(List(str))): list of output field name str
            extra_params(Optional(Dict)): extra params

        Returns:
            tuple: 2-element tuple containing
              * :class:`Status`: status
              * :class:`EntityData`: get result
        """
        return self._handler.get(collection_name, pk, output_fields, extra_params)

    def close(self):
        """
        Close connection.

        Returns: None
        """
        return self._handler.close()


class Client(BaseClient):
    def __init__(self, host, port=8100):
        """
        Constructor.

        Args:
            host (str): hostname
            port (int): port
        """

        handler = GrpcHandler(host, port)

        super().__init__(handler)

