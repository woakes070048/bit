# system
import logging

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# superset
from superset import db
from superset import app

# local
from bit.models.db_helper import ModelHelper
from bit.models import Connector

# from . import  GoogleDriveStorage

from .. datasources.campaign import CampaignPerformanceReportDataSource

DB_PREFIX = '{}'.format(
    app.config.get('APP_DB_PREFIX', 'bit'),
)

class AdWordsConnector(Connector):
    """AdWords: Model Auth connector"""

    __tablename__ = '{}_adwords_connector'.format(DB_PREFIX)  # sql table name

    # ForeignKey to Connector (Parent)
    id = Column(Integer, ForeignKey('bit_connectors.id'), primary_key=True)

    storage = relationship(
        'GoogleDriveStorage',
        # uselist=False,
        cascade='all,delete',
        back_populates='connector'
    )

    # storage = models.ForeignKey(GoogleDriveStorage)
    storage_path = Column(String(255), default='bit')

    __mapper_args__ = {
        'polymorphic_identity': 'adwords'
    }


    data_sources = (
        # GenderPerformanceReportDataSource,
        CampaignPerformanceReportDataSource,
        # GeoPerformanceReportDataSource,
        # PlacementPerformanceReportDataSource,
        # SearchQueryPerformanceReportDataSource,
        # PlaceHolderPerformanceReportDataSource,
    )

    @property
    def get_admin_data_sources(self):

        ds = frozenset([
            'GenderPerformanceReportDataSource',
            'CampaignPerformanceReportDataSource',
            'GeoPerformanceReportDataSource',
            'PlacementPerformanceReportDataSource',
            'SearchQueryPerformanceReportDataSource',
            'PlaceHolderPerformanceReportDataSource',
        ])

        return '<br/>'.join(ds)

    def get_data_sources(self):
        storage = self.storage[0]
        storage.init()
        for klass in self.data_sources:
            # change to get first storage
            yield klass(storage=storage, path=self.storage_path)

    def sync_adwords_campaign_performance_report(self):

        # print(self.storage[0])

        logging.info('Start sync adwords')
        for ds in self.get_data_sources():
            logging.info("Processing data source: {0}".format(ds.name))
            ds.sync()
        return {}

    # __mapper_args__ = {
    #     'concrete': True
    # }
