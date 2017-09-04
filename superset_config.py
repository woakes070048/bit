import os
from datetime import timedelta
from collections import OrderedDict

from flask import Blueprint
from werkzeug.contrib.cache import RedisCache


# override superset connectors
DEFAULT_MODULE_DS_MAP = OrderedDict([
    ('superset.connectors.sqla.models', ['SqlaTable']),
    # ('superset.connectors.druid.models', ['DruidDatasource']),
])

ADDITIONAL_MODULE_DS_MAP = {
    'bit.models': ['EtlTable'],
}

REDIS_ADDR = os.environ.get('REDIS_ADDR', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)


# CeleryConfig
class CeleryConfig(object):
    BROKER_URL = 'redis://{}:{}/0'.format(REDIS_ADDR, REDIS_PORT)
    CELERY_TIMEZONE = 'UTC'
    CELERY_IMPORTS = ('superset.sql_lab', 'bit.tasks')
    CELERYBEAT_SCHEDULE = {
        'add-every-30-seconds': {
            'task': 'bit.tasks.run_etl',
            'schedule': timedelta(seconds=30),
            'args': ()
        },
    }
    CELERY_RESULT_BACKEND = 'redis://{}:{}/0'.format(REDIS_ADDR, REDIS_PORT)
    CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}

CELERY_CONFIG = CeleryConfig

RESULTS_BACKEND = RedisCache(
    host=REDIS_ADDR,
    port=REDIS_PORT,
    key_prefix='superset_results'
)

CACHE_DEFAULT_TIMEOUT = 60 * 60 * 24
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': CACHE_DEFAULT_TIMEOUT,
    'CACHE_KEY_PREFIX': 'bit_',
    'CACHE_REDIS_HOST': REDIS_ADDR,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 1,
    'CACHE_REDIS_URL': 'redis://{}:{}/1'.format(REDIS_ADDR, REDIS_PORT)
}

# The MAX duration (in seconds) a query can run for before being killed
# by celery.
ETL_ASYNC_TIME_LIMIT_SEC = 60 * 60 * 6

# local static
static_page = Blueprint(
    'bit',
    __name__,
    url_prefix='/static',
    template_folder='bit/templates',
    static_folder='bit/static/bit',
    static_url_path='/bit'
)

BLUEPRINTS = [static_page]

try:
    from flask_appbuilder_config import *  # noqa
    import flask_appbuilder_config
    print('Loaded your flask_appbuilder configuration at [{}]'.format(
        security_config.__file__))
except ImportError:
    pass
