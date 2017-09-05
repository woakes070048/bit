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
from bit.utils.db_helper import ModelHelper
from bit.models import Connector

# from . import  GoogleDriveStorage

from .. datasources.campaign import CampaignPerformanceReportDataSource

from .. settings import CONNECTOR_INFO

DB_PREFIX = '{}'.format(
    app.config.get('APP_DB_PREFIX', 'bit'),
)

class AdWordsConnector(Connector):
    """AdWords: Model Auth connector"""

    __tablename__ = '{}_adwords_connector'.format(DB_PREFIX)

    __mapper_args__ = {
        'polymorphic_identity': 'adwords'
    }

    # ForeignKey to Connector (Parent)
    id = Column(Integer, ForeignKey('bit_connectors.id'), primary_key=True)

    storage = relationship(
        'GoogleDriveStorage',
        # uselist=False,
        cascade='all,delete',
        back_populates='connector'
    )

    storage_path = Column(String(255), default='bit')

    # no db fields/methods

    data_sources = CONNECTOR_INFO.get('reports')

    def connector_name(self):
        """ String: connector name. """
        return CONNECTOR_INFO.get('name', '')

    def connector_description(self):
        """ String: connector description. """
        return CONNECTOR_INFO.get('description', '')

    def connector_logo(self):
        """ String: connector name. """
        logo = '{}/{}/logo.png'.format(
            CONNECTOR_INFO.get('static_folder', ''),
            CONNECTOR_INFO.get('key', '')
        )
        return CONNECTOR_INFO.get('logo_pat', '').format(logo)

    def connector_info(self):
        """ String: connector info. """
        # change url
        html = '<h4><a href="/adwordsconnectorview/list/">{name}</a></h4>' \
               '{logo}' \
               '<p>{description}</p>'.format(
            name=self.connector_name(),
            logo=self.connector_logo(),
            description=self.connector_description(),
        )
        return html

    def admin_data_sources(self):
        """ List: data_sources(Reports) """

        reports = self.data_sources
        ds = [reports.get(report).get('name') for report in reports]

        html = '<p style="width:250px;">{}</p>'.format(
            '<br/>'.join(sorted(ds))
        )

        return html

    def get_data_sources(self):
        storage = self.storage[0]
        storage.init()
        for klass in self.data_sources:
            # change to get first storage
            yield klass(storage=storage, path=self.storage_path)

    def sync_adwords_campaign_performance_report(self):

        logging.info('Start sync adwords')
        for ds in self.get_data_sources():
            logging.info("Processing data source: {0}".format(ds.name))
            ds.sync()
        return {}
