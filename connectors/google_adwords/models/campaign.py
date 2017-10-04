# system
import logging

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import DateTime

# flask
from flask_appbuilder import Model


# local
from bit.utils.db_helper import ModelHelper


class CampaignPerformanceReport(Model, ModelHelper):
    """
    Model For Campaign Performance Report 
    https://developers.google.com/adwords/api/docs/appendix/reports
    /campaign-performance-report 
    """

    __tablename__ = 'bit_adwords_campaign_performance_report'  # sql table name

    id = Column(Integer, primary_key=True)
    campaign_id = Column(String(255))
    campaign_name = Column(String(255))
    cost = Column(Numeric, nullable=True)

    mobile_app_installs = Column(Integer, nullable=True)
    cost_per_mobile_app_installs = Column(Numeric, nullable=True)

    clicks = Column(Integer, nullable=True)
    impression_device = Column(String(255), index=True)
    impressions = Column(Numeric, nullable=True)
    conversions = Column(Numeric, nullable=True)
    date = Column(DateTime, nullable=True)
