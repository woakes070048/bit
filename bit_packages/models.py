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
from sqlalchemy import Numeric
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.mutable import MutableDict

# superset
from superset import sm

logger = logging.getLogger(__name__)


class Connector(Model):
    """Global BIT Connector."""

    __tablename__ = 'bit_connector'  # sql table name

    id = Column(Integer, primary_key=True)
    name = Column(String(255))  # connector name
    user_id = Column(Integer, ForeignKey('ab_user.id'))
    owner = relationship(
        sm.user_model,
        backref='facebook_connectors',
        foreign_keys=[user_id]
    )

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


# for test
class CorePerformanceReport(Model):

    __tablename__ = 'core_performancereport'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True)
    year = Column(Integer, index=True)
    month = Column(Integer, index=True)
    day = Column(Integer, index=True)
    name = Column(String(250), index=True)
    campaign_source = Column(String(250), index=True)
    campaign_name = Column(String(250), index=True)
    campaign_id = Column(String(250), index=True)
    clicks = Column(Integer)
    clicks_unique = Column(Integer)
    impressions = Column(Integer)
    conversions = Column(Integer)
    cost = Column(Numeric(17, 5))
    breakdowns = Column(MutableDict.as_mutable(HSTORE), index=True)
    measurements = Column(MutableDict.as_mutable(HSTORE), nullable=True)
