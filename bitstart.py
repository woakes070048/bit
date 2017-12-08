#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import warnings
from flask.exthook import ExtDeprecationWarning
warnings.simplefilter('ignore', ExtDeprecationWarning)


from flask_appbuilder import SQLA  # noqa
from superset import app  # noqa
from superset import migrate  # noqa
from superset import utils  # noqa
from superset.cli import manager  # noqa
from celery.bin import beat as celery_beat  # noqa

APP_DIR_NAME = 'bit'

BIT_APP_DIR = '{}/{}'.format(
    os.path.abspath(os.path.dirname(__file__)),
    APP_DIR_NAME
)


class AppManager(object):

    def __init__(self, app):
        self._app = app
        self._db_session = None

    def get_db(self):
        if self._db_session is None:
            self._db_session = SQLA(app)
        return self._db_session


app_manager = AppManager(app)

# override migrations directory
migrate.directory = BIT_APP_DIR + '/migrations'
app.extensions['migrate'].directory = BIT_APP_DIR + '/migrations'

config = app.config
celery_app = utils.get_celery_app(config)


@manager.command
def beat():

    cbeat = celery_beat.beat(app=celery_app)
    cbeat.run()


if __name__ == "__main__":
    manager.run()
