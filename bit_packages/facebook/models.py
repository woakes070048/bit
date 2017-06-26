# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

# system
import logging

# facebookads
# from facebookads import adobjects as fbO
from facebookads.adobjects.user import User as fbUser
from facebookads.adobjects.adaccount import AdAccount as fbAdAccount
from facebookads.adobjects.campaign import Campaign as fbAdCampaign
from facebookads.api import FacebookAdsApi

# flask_appbuilder
from flask_appbuilder import Model

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# local
from bit_packages.db_helper import ModelHelper
from bit_packages.models import Connector

from sync_fields import fb_ad_account_fields
from sync_fields import fb_ad_campaigns_fields
from sync_fields import fb_ad_set_fields


import config as fb_config


logger = logging.getLogger(__name__)


class FacebookConnector(Connector):
    """Facebook: Model Auth connector."""

    __tablename__ = 'bit_facebook_connector'  # sql table name

    _api_ = None

    connector_id = Column(Integer, ForeignKey('bit_connector.id'),
                          primary_key=True)
    ad_accounts = relationship('AdAccount', cascade='all,delete',
                               back_populates='connector')
    uid = Column(String(255), unique=True)
    access_token = Column(String(255))

    data_sources = (
        # InsightsPlacementImpressionDeviceDataSource,
        # InsightsAgeGenderDataSource,
        # InsightsAgeDataSource,
        # InsightsGenderDataSource,
        # InsightsCountryDataSource,
        # InsightsDevicePlatformImpressionDeviceDataSource
    )

    @property
    def api(self):
        """Singleton Api init."""

        if self._api_ is None:

            log_msg = '[{}] INIT API {}'.format(
                'Facebook',
                self.name
            )
            logger.info(log_msg)

            self._api_ = FacebookAdsApi.init(
                app_id=fb_config.fb_app_id,
                app_secret=fb_config.db_app_secret,
                access_token=self.access_token
            )
        return self._api_

    def sync_ad_accounts(self):
        """Synchronization Facebook AdAccount."""

        self.api  # move to init
        AdAccount.sync(connector=self)

    # def sync_init(self):
        # """Synchronization All."""

        # self.api  # move to init
        # batch = Batch(api=self.api)
        # AdAccount.sync(connector=self)
        # for ad_account in AdAccount.objects.filter(
        #         connector=self,synchronize=True):
        #     AdCampaign.sync(connector=self, batch=batch, account=ad_account)
        #     AdSet.sync(connector=self, batch=batch, account=ad_account)
        #     batch.execute()

    def get_data_sources(self):
        """Return All Data Sources for connector."""

        for data_source in self.data_sources:
            print(data_source)

        # for ad_account in AdAccount.objects.filter(connector=self,
        #                                            synchronize=True):
        #     FacebookAdsApi.set_default_account_id(ad_account.native_id)
        #     for data_source in self.data_sources:
        #         yield data_source(engine=self.api)


class AdAccount(Model, ModelHelper):
    """Facebook: Model for Ad Accounts."""

    __tablename__ = 'bit_facebook_ad_account'  # sql table name

    id = Column(Integer, primary_key=True)
    connector_id = Column(Integer, ForeignKey(
        'bit_facebook_connector.connector_id'
    ))
    connector = relationship('FacebookConnector', back_populates='ad_accounts')
    ad_campaigns = relationship('AdCampaign', cascade='all,delete',
                                back_populates='ad_account')
    native_id = Column(String(255), unique=True, index=True)
    account_id = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    account_status = Column(Integer)
    synchronize = Column(Boolean, default=True)
    balance = Column(Numeric)
    timezone_offset_hours_utc = Column(Numeric)
    amount_spent = Column(Numeric)

    def __repr__(self):
        """Object name."""

        return self.native_id

    def sync_ad_campaigns(self):
        """Synchronization Facebook Ad Campaigns."""

        # Check to need Synchronize
        if self.synchronize:

            log_msg = '[{}] sync_ad_campaigns {}'.format(
                'Facebook',
                self.name
            )

            logger.info(log_msg)

            self.connector.api

            fb_ad_account = fbAdAccount(fbid=self.native_id)
            fb_ad_campaigns = fb_ad_account.get_campaigns(
                # pending=True,
                fields=fb_ad_campaigns_fields
            )

            for fb_ad_campaign in fb_ad_campaigns:

                obj, created = AdCampaign.update_or_create(
                    ad_account=self,
                    native_id=fb_ad_campaign[fbAdCampaign.Field.id],
                    defaults=fb_ad_campaign,
                    remove_id=True
                )

    @classmethod
    def sync(cls, connector):
        """Synchronization All Facebook"""

        # get Facebook User
        fb_user = fbUser(fbid='me')

        # get exist accounts from Facebook
        fb_ad_accounts = fb_user.get_ad_accounts(
            fields=fb_ad_account_fields  # request fields
        )

        for fb_ad_account in fb_ad_accounts:
            """Iterate accounts and save."""

            obj, created = cls.update_or_create(
                connector=connector,
                account_id=fb_ad_account[fbAdAccount.Field.account_id],
                native_id=fb_ad_account[fbAdAccount.Field.id],
                defaults=fb_ad_account,
                remove_id=True
            )

class AdCampaign(Model, ModelHelper):
    """Facebook: Model for Ad Campaigns."""

    __tablename__ = 'bit_facebook_ad_campaigns'  # sql table name

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('bit_facebook_ad_account.id'))
    ad_account = relationship('AdAccount', back_populates='ad_campaigns')

    native_id = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    configured_status = Column(String(255))
    effective_status = Column(String(255))
    objective = Column(String(255))
    spend_cap = Column(String(255))
    status = Column(String(255), index=True)
    buying_type = Column(String(255))
    budget_rebalance_flag = Column(Boolean)
    can_use_spend_cap = Column(Boolean)
    start_time = Column(DateTime, nullable=True)
    stop_time = Column(DateTime, nullable=True)
    created_time = Column(DateTime)
    updated_time = Column(DateTime)

    def __repr__(self):
        return self.name


    def sync_ad_campaigns(self):
        """Synchronization Facebook Ad Campaigns."""


        # self.api  # move to init
        # AdAccount.sync(connector=self)

        print('sync_ad_campaigns')

    @classmethod
    def sync(cls, connector):
        """Synchronization All Facebook Ad Campaigns."""

        pass


class AdSet(Model, ModelHelper):
    """Facebook: Model for Ad Set."""

    __tablename__ = 'bit_facebook_ad_sets'  # sql table name

    id = Column(Integer, primary_key=True)

    # campaign = models.ForeignKey(AdCampaign)

    name = Column(String(255))
    native_id = Column(String(255), unique=True, index=True)
    billing_event = Column(String(255))
    budget_remaining = Column(String(255))
    configured_status = Column(String(255))
    daily_budget = Column(String(255))
    effective_status = Column(String(255))
    lifetime_budget = Column(String(255))
    optimization_goal = Column(String(255))
    status = Column(String(255), index=True)
    bid_amount = Column(Integer, nullable=True)
    frequency_cap = Column(Integer, nullable=True)
    frequency_cap_reset_period = Column(Integer, nullable=True)
    lifetime_frequency_cap = Column(Integer, nullable=True)
    lifetime_imps = Column(Integer)
    is_autobid = Column(Boolean)
    is_average_price_pacing = Column(Boolean)
    recurring_budget_semantics = Column(Boolean)
    rtb_flag = Column(Boolean)
    use_new_app_click = Column(Boolean)
    end_time = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
