# system
import logging

# facebookads
from facebookads.api import FacebookAdsApi

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# local
from bit.models import Connector

from fb import AdAccount
from .. settings import CONNECTOR_INFO as CI


class FacebookConnector(Connector):
    """Facebook: Model Auth connector"""

    __tablename__ = '{}_{}'.format(
        CI.get('table_prefix', ''), 'connector'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'facebook_ads'
    }

    # ForeignKey to Connector (Parent)
    id = Column(Integer, ForeignKey('bit_connectors.id'), primary_key=True)

    # Back relation from Connector To FacebookConnector (Children)
    ad_accounts = relationship(
        'AdAccount',
        cascade='all,delete',
        back_populates='connector'
    )

    # data fields
    uid = Column(String(255), unique=True)
    access_token = Column(String(255))

    # no db fields/methods

    _api_ = None

    data_sources = CI.get('reports')

    def connector_name(self):
        """ String: connector name. """
        return CI.get('name', '')

    def connector_description(self):
        """ String: connector description. """
        return CI.get('description', '')

    def connector_logo(self):
        """ String: connector name. """
        logo = '{}/{}/logo.png'.format(
            CI.get('static_folder', ''),
            CI.get('key', '')
        )
        return CI.get('logo_pat', '').format(logo)

    def connector_info(self):
        """ String: connector info. """
        # change url
        html = '<h4><a href="/facebookconnectorview/list/">{name}</a></h4>' \
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

    @property
    def api(self):
        """Singleton Api init."""

        if self._api_ is None:

            log_msg = '[{}] INIT API {}'.format(
                'Facebook',
                self.name
            )
            logging.info(log_msg)

            self._api_ = FacebookAdsApi.init(
                app_id=CI.get('app_id'),
                app_secret=CI.get('app_secret'),
                access_token=self.access_token
            )
        return self._api_

    def sync_ad_accounts(self):
        """Synchronization Facebook AdAccount."""

        self.api  # move to init
        AdAccount.sync(connector=self)
