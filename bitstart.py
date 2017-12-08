#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import warnings
from flask.exthook import ExtDeprecationWarning
warnings.simplefilter('ignore', ExtDeprecationWarning)


# from superset import db
from flask_appbuilder import SQLA
from superset import app
from superset import migrate
from superset import utils
from superset import viz
from superset.cli import manager
from celery.bin import beat as celery_beat
from custom_viz import custom_viz_types

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
app.static_folder = BIT_APP_DIR + '/static'

#################################################################
# Handling manifest file logic at app start
#################################################################
MANIFEST_FILE = BIT_APP_DIR + '/static/assets/dist/manifest.json'
manifest = {}


def parse_manifest_json():
    global manifest

    try:
        with open(MANIFEST_FILE, 'r') as f:
            manifest = json.load(f)
    except Exception:
        print("no manifest file found at " + MANIFEST_FILE)


def get_manifest_file(filename):
    if app.debug:
        parse_manifest_json()
    return '/static/assets/dist/' + manifest.get(filename, '')


parse_manifest_json()


@app.context_processor
def get_js_manifest():
    return dict(js_manifest=get_manifest_file)


config = app.config

# viz.viz_types = dict(viz.viz_types)
viz.viz_types.update(custom_viz_types)

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
