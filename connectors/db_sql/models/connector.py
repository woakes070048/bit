# system
# import zlib
# import logging
# import os
# import urllib3
# import petl
# from datetime import datetime, timedelta

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

# superset
# from superset import cache

# local
from bit.models import Connector

CONNECTOR_NAME = 'sql_db'


class SQLDBConnector(Connector):

    __tablename__ = 'bit_{}_connector'.format(CONNECTOR_NAME)  # sql table name

    # ForeignKey to Connector (Parent)
    id = Column(Integer, ForeignKey('bit_connectors.id'), primary_key=True)

    # extra
    app_id = Column(String(255))
    api_token = Column(String(255))
    url_pat = Column(String(255))

    __mapper_args__ = {
        'polymorphic_identity': CONNECTOR_NAME
    }

    tables = [
        'dasdas2321',
        'dasdas',
    ]

    @property
    def get_admin_data_sources(self):
        """ List: data_sources(Reports) """
        return self.tables

    def get_columns(self):
        return ['dsadasda']
