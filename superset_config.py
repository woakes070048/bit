# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from flask import Blueprint

"""
hard fix for (sqlalchemy: 'InstrumentedList' object in falsk app builder)
widget show list objects error utf-8
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')

SUPERSET_WEBSERVER_PORT = os.environ.get("PORT", "5008")

SUPERSET_WORKERS = os.environ.get('WORKERS', 4)

APP_NAME = 'Codesmart BIT'
APP_ICON = '/static/bit/images/codesmart_bit.png'

# Superset specific config
ROW_LIMIT = 5000

ADDITIONAL_MODULE_DS_MAP = {
    'bit_packages.models': ['BitPackages'],
}

# AUTH_TYPE = 0
# OPENID_PROVIDERS = []

AUTH_TYPE = 1  # Database Authentication
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = 'Public'

# Config for Flask-WTF Recaptcha necessary for user registration
RECAPTCHA_PUBLIC_KEY = 'GOOGLE PUBLIC KEY FOR RECAPTCHA'
RECAPTCHA_PRIVATE_KEY = 'GOOGLE PRIVATE KEY FOR RECAPTCHA'

# Config for Flask-Mail necessary for user registration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_USE_TLS = True
MAIL_USERNAME = 'yourappemail@gmail.com'
MAIL_PASSWORD = 'passwordformail'
MAIL_DEFAULT_SENDER = 'fabtest10@gmail.com'

CSRF_ENABLED = True
SECRET_KEY = 'q13221wdaser423ty23423%$^@$#$@#iop'
MAPBOX_API_KEY = ''

# fb access
FB_APP_ID = 'FB_APP_ID'
FB_APP_SECRET = 'FB_APP_SECRET'


# local static
static_page = Blueprint(
    'bit',
    __name__,
    url_prefix='/static',
    template_folder='templates',
    static_folder='static/bit',
    static_url_path='/bit'
)

BLUEPRINTS = [static_page]

try:
    from security_config import *  # noqa
    import security_config
    print('Loaded your security configuration at [{}]'.format(
        security_config.__file__))
except ImportError:
    pass
