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


# from superset import db
from superset import app
from superset import migrate
from superset import utils
from superset.cli import manager
from celery.bin import beat as celery_beat


APP_DIR_NAME = 'bit'

BIT_APP_DIR = '{}/{}'.format(
    os.path.abspath(os.path.dirname(__file__)),
    APP_DIR_NAME
)

# override migrations directory
migrate.directory = BIT_APP_DIR + '/migrations'
app.extensions['migrate'].directory = BIT_APP_DIR + '/migrations'
config = app.config
celery_app = utils.get_celery_app(config)


# @manager.command
# def chiter():
#     print('CHITER START')
#     from bit_packages.etl.models import EtlTable
#
#     etl_table = db.session.query(EtlTable).filter_by()
#
#     print('CHITER END')


@manager.command
def beat():

    cbeat = celery_beat.beat(app=celery_app)
    cbeat.run()


if __name__ == "__main__":
    manager.run()
