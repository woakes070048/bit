# -*- coding: utf-8 -*-
from __future__ import absolute_import

from superset import app
config = app.config

fb_app_id = config.get('FB_APP_ID', 'FB_APP_ID')
db_app_secret = config.get('FB_APP_SECRET', 'FB_APP_SECRET')
