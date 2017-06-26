# -*- coding: utf-8 -*-
from __future__ import absolute_import

# system
import logging

# flask_appbuilder
from flask_appbuilder import Model

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

logger = logging.getLogger(__name__)


class Connector(Model):
    """Global BIT Connector."""

    __tablename__ = 'bit_connector'  # sql table name

    id = Column(Integer, primary_key=True)
    name = Column(String(255))  # connector name

    def __repr__(self):
        """Object name."""

        return self.name

    def get_data_sources(self):
        """Return All Data Sources for connector."""

        raise NotImplementedError()

    def sync(self):
        """Run Synchronization for All connector Data Sources."""

        for data_source in self.get_data_sources():
            log_msg = 'Processing data source: {0}'.format(data_source.name)
            logger.info(log_msg)
            data_source.sync()


class BitMetric(Model):
    """Default Metric Class For Superset Init."""

    __tablename__ = 'bit_metric'  # sql table name

    id = Column(Integer, primary_key=True)


class BitPackages(Model):
    """Default DataSource Class For Superset Init."""

    __tablename__ = 'bit_packages'  # sql table name

    type = 'package'
    metric_class = BitMetric

    id = Column(Integer, primary_key=True)
