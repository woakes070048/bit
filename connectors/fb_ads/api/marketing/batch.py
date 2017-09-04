# system
import copy
import logging

# facebook ads
from facebookads.api import FacebookAdsApiBatch, Cursor


logger = logging.getLogger(__name__)


class Batch(FacebookAdsApiBatch):

    @classmethod
    def parse_response(cls, request, response):
        params = copy.deepcopy(request._params)
        if request._api_type == 'EDGE' and request._method == 'GET':
            cursor = Cursor(
                target_objects_class=request._target_class,
                params=params,
                fields=request._fields,
                include_summary=request._include_summary,
                api=request._api,
                node_id=request._node_id,
                endpoint=request._endpoint,
            )
            cursor.load_next_page()
            return cursor

        if response.error():
            raise response.error()
        if request._response_parser:
            return request._response_parser.parse_single(response.json())
        else:
            return response

    def add_request(
        self,
        request,
        success=None,
        failure=None,
    ):
        def callback_success(response):
            if success:
                response = self.parse_response(
                    request=request, response=response)
                success(response=response)

        def callback_failure(response):
            if failure:
                failure(error=response.error())

        return super(Batch, self).add_request(
            request=request, success=callback_success,
            failure=callback_failure)


class BatchSync(object):

    @classmethod
    def from_object(cls, connector, obj):
        raise NotImplementedError()

    @classmethod
    def sync_success(cls, response, connector):
        logger.info('Sync {0}'.format(cls.__name__))
        for obj in response:
            cls.from_object(connector=connector, obj=obj)

    @classmethod
    def sync_failure(cls, error, connector):
        logger.error('Sync failure {0} {1}'.format(cls.__name__, error))

    @classmethod
    def batch_sync(cls, connector, batch, request):

        def callback_success(response):
            cls.sync_success(response=response, connector=connector)

        def callback_failure(error):
            cls.sync_failure(error=error, connector=connector)

        batch.add_request(
            request=request,
            success=callback_success,
            failure=callback_failure
        )
