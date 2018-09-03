# system
import os
import logging
import time
import datetime
import petl
import requests
from dateutil import parser

# facebook_business
from facebook_business.adobjects.user import User as fbUser
from facebook_business.adobjects.adaccount import AdAccount as fbAdAccount
from facebook_business.adobjects.campaign import Campaign as fbAdCampaign
from facebook_business.adobjects.adset import AdSet as fbAdSet
from facebook_business.adobjects.ad import Ad as fbAd
from facebook_business.adobjects.adsinsights import AdsInsights as fbAdsInsights
from facebook_business.adobjects.adreportrun import AdReportRun as fbAdReportRun

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
from sqlalchemy.ext.declarative import declared_attr

# superset
from superset import db

# local
from bit.utils.db_helper import ModelHelper
from bit.models import PerformanceReport

# fb
from .. api.marketing import Batch
from .. sync_fields import fb_ad_account_fields
from .. sync_fields import fb_ad_campaign_fields
from .. sync_fields import fb_ad_set_fields
from .. sync_fields import fb_ad_fields
from .. sync_fields import fb_ads_insight_fields


logger = logging.getLogger(__name__)


class AdAccount(Model, ModelHelper):
    """Facebook: Model for Ad Accounts."""

    __tablename__ = 'bit_facebook_ad_account'  # sql table name

    id = Column(Integer, primary_key=True)

    # ForeignKey to FacebookConnector (Parent)
    # fb_connector_id
    connector_id = Column(Integer, ForeignKey(
        'bit_connectors.id'
    ))

    # Back relation to FacebookConnector
    # fb_connector
    connector = relationship('FacebookConnector', back_populates='ad_accounts')

    # Back relation to AdCampaign
    ad_campaigns = relationship('AdCampaign', cascade='all,delete',
                                back_populates='ad_account')

    # from FB
    native_id = Column(String(255), unique=True, index=True)  # id
    account_id = Column(String(255), unique=True, index=True)
    name = Column(String(255))

    amount_spent = Column(Numeric)
    balance = Column(Numeric)
    timezone_offset_hours_utc = Column(Numeric)
    account_status = Column(Integer)
    synchronize = Column(Boolean, default=True)
    from_date = Column(String(255))
    to_date = Column(String(255))

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
                fields=fb_ad_campaign_fields
            )
            for fb_ad_campaign in fb_ad_campaigns:

                obj, created = AdCampaign.update_or_create(
                    ad_account=self,
                    native_id=fb_ad_campaign[fbAdCampaign.Field.id],
                    defaults=fb_ad_campaign,
                    remove_id=True
                )

    def sync_all_ad_sets(self):
        """Synchronization Facebook All Ad Sets."""

        self.connector.api

        fb_ad_account = fbAdAccount(fbid=self.native_id)
        fb_ad_sets = fb_ad_account.get_ad_sets(
            # pending=True,
            fields=fb_ad_set_fields
        )

        for fb_ad_set in fb_ad_sets:
            ad_campaign_id=db.session.query(AdCampaign.id).filter_by(
                native_id=fb_ad_set[fbAdSet.Field.campaign_id]
            ).scalar()

            if not ad_campaign_id:
                self.sync_ad_campaigns()
                ad_campaign_id = db.session.query(AdCampaign.id).filter_by(
                    native_id=fb_ad_set[fbAdSet.Field.campaign_id]
                ).scalar()

            obj, created = AdSet.update_or_create(
                ad_campaign_id=ad_campaign_id,
                native_id=fb_ad_set[fbAdSet.Field.id],
                defaults=fb_ad_set,
                remove_id=True
            )

    def sync_all_ads(self):
        """Synchronization Facebook All Ads."""

        self.connector.api

        fb_ad_account = fbAdAccount(fbid=self.native_id)
        fb_ads = fb_ad_account.get_ads(
            # pending=True,
            fields=fb_ad_fields
        )

        for fb_ad in fb_ads:
            ad_set_id = db.session.query(AdSet.id).filter_by(
                native_id=fb_ad[fbAd.Field.adset_id]
            ).scalar()

            if not ad_set_id:
                self.sync_all_ad_sets()
                ad_set_id = db.session.query(AdSet.id).filter_by(
                    native_id=fb_ad[fbAd.Field.adset_id]
                ).scalar()

            obj, created = Ad.update_or_create(
                ad_set_id=ad_set_id,
                native_id=fb_ad[fbAd.Field.id],
                defaults=fb_ad,
                remove_id=True
            )

    def sync_ads_insights(self):
        """Synchronization Facebook All Ads."""

        self.connector.api
        fb_ad_account = fbAdAccount(fbid=self.native_id)

        # DATA_SOURCE_START_DATE = '2018-01-30'

        # since = parser.parse(DATA_SOURCE_START_DATE).date()

        # until = since + datetime.timedelta(days=7)

        now = datetime.datetime.now().date()
        yesterday = now - datetime.timedelta(days=1)

        since = parser.parse(self.from_date).date()

        if since > yesterday:
            return None

        until = parser.parse(self.to_date).date()

        until = min(until, yesterday)
        time_range = {
            'since': since.isoformat(),
            'until': until.isoformat()
        }

        breakdowns = (
            fbAdsInsights.Breakdowns.impression_device,
            # fbAdsInsights.Breakdowns.age,
            # fbAdsInsights.Breakdowns.gender,
        )

        report_name = '30fdsfds2432423'

        logger.info(
            "Run report '{0}' since: {1} until: {2}".format(report_name, since,
                                                            until))
        filename = "{0}_{1}_{2}.csv".format(report_name, since, until)

        if not os.path.exists(filename):

            request = fb_ad_account.get_insights(
                # pending=True,
                async=True,
                fields=fb_ads_insight_fields,
                params={
                    'time_increment': 1,
                    # 'limit': 1,
                    'level': fbAdsInsights.Level.ad,
                    'breakdowns': breakdowns,
                    'time_range': time_range
                }
            )

            while True:
                time.sleep(10)
                job = request.remote_read()
                logger.info("Report run progress: {0}%".format(
                    job[fbAdReportRun.Field.async_percent_completion])
                )
                if job:
                    logger.info("Report is ready")
                    break

            logger.info("Download report '{0}' since: {1} until: {2}".format(
                self.name, since,until
            ))

            # logger.info(request)
            # logger.info(self.connector.access_token)
            # logger.info(request['report_run_id'])

            response = requests.get(
                url="https://www.facebook.com/ads/ads_insights/export_report",
                params={
                    'report_run_id': request['report_run_id'],
                    'format': 'csv',
                    'access_token': self.connector.access_token
                },
                headers={
                    'Accept-Language': 'en'
                }
            )

            with open(filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024):
                    fd.write(chunk)

        table = petl.io.fromcsv(filename)
        if table.len() == 2 and table[1][0] == 'No data available.':
            logger.info('No data available.')
            return []

        logger.info(table.len())

        if table.len() < 20:
            logger.info(table)

        for fb_insight in petl.dicts(table).list():
            if 'Ad ID' in fb_insight:

                ad_id = db.session.query(Ad.id).filter_by(
                    native_id=fb_insight['Ad ID']
                ).scalar()

                fb_insight['account_id'] = fb_insight['Account ID']
                fb_insight['adset_id'] = fb_insight['Ad Set ID']
                fb_insight['campaign_id'] = fb_insight['Campaign ID']
                fb_insight['campaign_name'] = fb_insight['Campaign Name']

                fb_insight['mobile_app_installs'] = fb_insight[
                    'Mobile App Installs']
                fb_insight['cost_per_mobile_app_installs'] = 0

                fb_insight['mobile_app_purchases'] = fb_insight[
                    'Mobile App Purchases']
                fb_insight['cost_per_mobile_app_purchases'] = 0

                fb_insight['cost'] = fb_insight['Amount Spent (USD)']

                if fb_insight['cost']:

                    if fb_insight['mobile_app_installs']:
                        try:
                            fb_insight['cost_per_mobile_app_installs'] = \
                                float(fb_insight['cost']) / float(fb_insight['mobile_app_installs'])
                        except:
                            pass
                    else:
                        fb_insight['mobile_app_installs'] = 0

                    if fb_insight['mobile_app_purchases']:
                        try:
                            fb_insight['cost_per_mobile_app_purchases'] = \
                                float(fb_insight['cost']) / float(fb_insight['mobile_app_purchases'])
                        except:
                            pass
                    else:
                        fb_insight['mobile_app_purchases'] = 0

                fb_insight['unique_clicks'] = fb_insight['Unique Clicks (All)']
                fb_insight['cost_per_unique_click'] = fb_insight['Cost per Unique Click (All) (USD)']
                fb_insight['impression_device'] = fb_insight['Impression Device']
                fb_insight['unique_impressions'] = fb_insight['Impressions']

                # Mobile App Actions Conversion Value
                # fb_insight['age'] = fb_insight['Age']
                # fb_insight['gender'] = fb_insight['Gender']

                fb_insight['date_start'] = fb_insight['Reporting Starts']
                fb_insight['date_stop'] = fb_insight['Reporting Ends']

                date = parser.parse(fb_insight['date_start']).date()

                obj, created = DailyAdInsightsImpressionDevice.update_or_create(
                    ad_id=ad_id,
                    date_start=fb_insight['date_start'],
                    date_stop=fb_insight['date_stop'],
                    cost=fb_insight['cost'],
                    unique_clicks=fb_insight['unique_clicks'],
                    # native_id=fb_insight['ID'],
                    defaults = fb_insight,
                    remove_id = True
                )

                obj, created = PerformanceReport.update_or_create(
                    date=date,
                    year=date.year,
                    month=date.month,
                    day=date.day,
                    name='impression_device',
                    campaign_source='facebook',
                    campaign_name=fb_insight['campaign_name'],
                    campaign_id=fb_insight['campaign_id'],
                    clicks=0,
                    clicks_unique=fb_insight['unique_clicks'],
                    impressions=fb_insight['unique_impressions'],
                    conversions=0,
                    cost=fb_insight['cost'],
                    mobile_app_installs=fb_insight['mobile_app_installs'],
                    mobile_app_purchases=fb_insight['mobile_app_purchases'],
                    cost_per_mobile_app_installs=fb_insight['cost_per_mobile_app_installs'],
                    cost_per_mobile_app_purchases=fb_insight['cost_per_mobile_app_purchases'],
                    # breakdowns=breakdowns,
                    breakdowns=dict(device=fb_insight['impression_device']),
                    # measurements=dict(fb_insight),
                    defaults=fb_insight,
                    remove_id=True,
                    # remove_id=True
                )

        return petl.dicts(table).list()

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

    # ForeignKey to AdAccount (Parent)
    ad_account_id = Column(Integer, ForeignKey('bit_facebook_ad_account.id'))

    # Back relation to AdAccount
    ad_account = relationship('AdAccount', back_populates='ad_campaigns')

    # Back relation to AdSet
    ad_adsets = relationship('AdSet', cascade='all,delete',
                             back_populates='ad_campaign')

    # data fields:

    # from FB
    native_id = Column(String(255), unique=True, index=True)  # id
    account_id = Column(String(255))
    name = Column(String(255))

    budget_rebalance_flag = Column(Boolean)
    buying_type = Column(String(255))
    spend_cap = Column(String(255))
    can_use_spend_cap = Column(Boolean)
    configured_status = Column(String(255))
    effective_status = Column(String(255))
    objective = Column(String(255))
    status = Column(String(255), index=True)
    start_time = Column(DateTime, nullable=True)
    stop_time = Column(DateTime, nullable=True)
    created_time = Column(DateTime)
    updated_time = Column(DateTime)

    def __repr__(self):
        return self.name

    def sync_ad_sets(self):
        """Synchronization Facebook Ad Sets."""

        log_msg = '[{}] sync_ad_sets {}'.format(
            'Facebook',
            self.name
        )

        logger.info(log_msg)

        self.ad_account.connector.api

        fb_ad_campaign = fbAdCampaign(fbid=self.native_id)
        fb_ad_sets = fb_ad_campaign.get_ad_sets(
            # pending=True,
            fields=fb_ad_set_fields
        )

        for fb_ad_set in fb_ad_sets:
            obj, created = AdSet.update_or_create(
                ad_campaign=self,
                native_id=fb_ad_set[fbAdSet.Field.id],
                defaults=fb_ad_set,
                remove_id=True
            )

    @classmethod
    def sync(cls, connector):
        """Synchronization All Facebook Ad Campaigns."""

        pass


class AdSet(Model, ModelHelper):
    """Facebook: Model for Ad Set."""

    __tablename__ = 'bit_facebook_ad_sets'  # sql table name

    id = Column(Integer, primary_key=True)

    # ForeignKey to AdCampaign (Parent)
    ad_campaign_id = Column(Integer, ForeignKey('bit_facebook_ad_campaigns.id'))

    # Back relation to AdCampaign
    ad_campaign = relationship('AdCampaign', back_populates='ad_adsets')

    # Back relation to AdSet
    ad_ads = relationship('Ad', cascade='all,delete',
                          back_populates='ad_set')

    # data fields:

    # from FB
    native_id = Column(String(255), unique=True, index=True)  # id
    account_id = Column(String(255))
    campaign_id = Column(String(255))
    name = Column(String(255))

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

    def __repr__(self):
        return self.name

    def sync_ads(self):
        """Synchronization Facebook Ad."""

        log_msg = '[{}] sync_ads {}'.format(
            'Facebook',
            self.name
        )

        logger.info(log_msg)

        self.ad_campaign.ad_account.connector.api

        fb_ad_set = fbAdSet(fbid=self.native_id)
        fb_ads = fb_ad_set.get_ads(
            # pending=True,
            fields=fb_ad_fields
        )

        for fb_ad in fb_ads:

            obj, created = Ad.update_or_create(
                ad_set=self,
                native_id=fb_ad[fbAd.Field.id],
                defaults=fb_ad,
                remove_id=True
            )

    @classmethod
    def sync(cls, connector):
        """Synchronization All Facebook Ad Campaigns."""
        pass


class RefDailyAdInsightsMixin(object):

    # ForeignKey to Ad (Parent)
    @declared_attr
    def ad_id(cls):
        return Column(Integer, ForeignKey('bit_facebook_ad.id'))

    # Back relation from Ad To DailyAdInsight (Children)
    @declared_attr
    def ad(cls):
        return relationship('Ad')


class Ad(Model, ModelHelper):
    """Facebook: Model for Ad."""

    __tablename__ = 'bit_facebook_ad'  # sql table name

    id = Column(Integer, primary_key=True)

    # ForeignKey to AdSet (Parent)
    ad_set_id = Column(Integer, ForeignKey('bit_facebook_ad_sets.id'))
    # Back relation from AdSet To Ad (Children)
    ad_set = relationship('AdSet', back_populates='ad_ads')

    # Back relation to Ad
    # ad_insights = relationship('DailyAdInsights', cascade='all,delete',
    #                            back_populates='ad')

    # data fields:
    # from FB
    native_id = Column(String(255), unique=True, index=True)  # id
    account_id = Column(String(255))
    campaign_id = Column(String(255))
    adset_id = Column(String(255))
    name = Column(String(255))

    bid_amount = Column(Integer, nullable=True)
    bid_info = Column(String(255))
    bid_type = Column(String(255))  # change to hstore
    configured_status = Column(String(255))
    effective_status = Column(String(255))
    status = Column(String(255))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)

    # conversion_specs list<ConversionActionQuery>
    # https://developers.facebook.com/docs/marketing-api/
    # reference/conversion-action-query/

    # creative AdCreative
    # https://developers.facebook.com/docs/marketing-api/reference/ad-creative/

    def __repr__(self):
        return self.name


class DailyAdInsights(ModelHelper):

    """Facebook: Model for DailyAdInsights. Abstract Table"""

    __tablename__ = None  # {breakdown_name}_insights

    # # ForeignKey to Ad (Parent)
    # @declared_attr
    # def ad_id(self):
    #     return Column(Integer, ForeignKey('bit_facebook_ad.id'))

    # # Back relation from Ad To DailyAdInsight (Children)
    # @declared_attr
    # def ad(self):
    #     return relationship('Ad', back_populates='ad_insights')

    # Columns
    id = Column(Integer, primary_key=True)

    # data fields:
    # from FB

    account_id = Column(String(255))
    campaign_id = Column(String(255))
    adset_id = Column(String(255))

    campaign_name = Column(String(255))

    cost = Column(Numeric, nullable=True)

    mobile_app_installs = Column(Integer, nullable=True)
    mobile_app_purchases = Column(Integer, nullable=True)

    cost_per_mobile_app_installs = Column(Numeric, nullable=True)
    cost_per_mobile_app_purchases = Column(Numeric, nullable=True)

    spend = Column(Numeric, nullable=True)

    cost_per_unique_click = Column(Numeric, nullable=True)
    unique_clicks = Column(Integer, nullable=True)
    unique_impressions = Column(Integer, nullable=True)
    unique_social_clicks = Column(Integer, nullable=True)
    unique_social_impressions = Column(Integer, nullable=True)
    website_clicks = Column(Integer, nullable=True)

    date_start = Column(DateTime, nullable=True)
    date_stop = Column(DateTime, nullable=True)

    # placement


class DailyAdInsightsImpressionDevice(DailyAdInsights, RefDailyAdInsightsMixin,
                                      Model):

    __tablename__ = 'bit_facebook_daily_ad_insights_impression_device'  # sql table name

    impression_device = Column(String(255), index=True)

    breakdowns = (
        # fbAdsInsights.Breakdowns.placement,  # remove in new version api
        fbAdsInsights.Breakdowns.impression_device,
    )

    # class Meta:
        # unique_together = ('ad', 'date', 'impression_device')
        # db_table = 'facebook_insights_daily_p_id'


#
# class DailyAdInsights(Model, ModelHelper):
#
#
#     __tablename__ = 'bit_facebook_daily_ad_insights'  # sql table name
#
#
#     # ForeignKey to Ad (Parent)
#     ad_id = Column(Integer, ForeignKey('bit_facebook_ad.id'))
#     # Back relation from Ad To DailyAdInsight (Children)
#     ad = relationship('Ad', back_populates='ad_insights')
#
#
# class DailyAdInsights(Model, ModelHelper):
#     """Facebook: Model for DailyAdInsights."""
#
#     __abstract__ = True
#
#
