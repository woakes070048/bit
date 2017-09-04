# system
# import logging

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.mutable import MutableDict

# flask
from flask_appbuilder import Model

# superset
from superset import app

# locale
from db_helper import ModelHelper


DB_PREFIX = '{}'.format(
    app.config.get('APP_DB_PREFIX', 'bit'),
)


class PerformanceReport(Model, ModelHelper):

    __tablename__ = '{}_performance_report'.format(DB_PREFIX)  # sql table name

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

    mobile_app_installs = Column(Integer, nullable=True)
    mobile_app_purchases = Column(Integer, nullable=True)

    cost_per_mobile_app_installs = Column(Numeric, nullable=True)
    cost_per_mobile_app_purchases = Column(Numeric, nullable=True)

    breakdowns = Column(MutableDict.as_mutable(HSTORE), index=True)
    measurements = Column(MutableDict.as_mutable(HSTORE), nullable=True)
