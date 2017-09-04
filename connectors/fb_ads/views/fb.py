# system
import logging
import httplib2
import json

# flask
from flask import redirect

# flask_appbuilder
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.actions import action

# flask_babel
from flask_babel import gettext as __

# superset
from superset import appbuilder
from superset.views.base import SupersetModelView, DeleteMixin

# local
from .. models.fb import FacebookConnector
from .. models.fb import AdAccount
from .. models.fb import AdCampaign
from .. models.fb import AdSet
from .. models.fb import Ad
from .. models.fb import DailyAdInsightsImpressionDevice
from .. import config as fb_config


class FacebookConnectorView(SupersetModelView, DeleteMixin):
    """View For Facebook FacebookConnector Model."""

    datamodel = SQLAInterface(FacebookConnector)

    list_columns = [
        'name',
        'uid',
        'get_admin_data_sources',
    ]

    # add_template = 'bit_packages/facebook/templates/add_connector.html'
    add_template = 'facebook/add_connector.html'

    add_columns = ['name', 'uid', 'access_token']

    edit_columns = add_columns

    def pre_add(self, obj):
        """Check data before save"""

        if obj.access_token == '':
            raise Exception('Enter a access_token')

        lat_uri = 'https://graph.facebook.com/oauth/access_token?'\
                  'client_id={APP_ID}&'\
                  'client_secret={APP_SECRET}&'\
                  'grant_type=fb_exchange_token&'\
                  'fb_exchange_token={EXISTING_ACCESS_TOKEN}'.format(
                      APP_ID=fb_config.fb_app_id,
                      APP_SECRET=fb_config.db_app_secret,
                      EXISTING_ACCESS_TOKEN=obj.access_token,
                  )

        if lat_uri:
            h = httplib2.Http(".cache")
            (resp, content) = h.request(lat_uri, 'GET',
                            headers={'cache-control':'no-cache'})
            if 'access_token' in content:
                json_content = json.loads(content)
                if 'access_token' in json_content:
                    logging.info(json_content['access_token'])
                    obj.access_token = json_content['access_token']

    # actions
    @action('sync_ad_accounts', 'Sync AdAccounts for this connector',
            'Sync AdAccounts for this connector', 'fa-rocket')
    def sync_ad_accounts(self, item):
        """Call sync_ad_accounts."""
        item[0].sync_ad_accounts()

        return redirect('adaccountview/list/')


class AdAccountView(SupersetModelView, DeleteMixin):
    """View For Facebook AdAccount Model."""

    datamodel = SQLAInterface(AdAccount)

    list_columns = ['connector', 'name', 'synchronize']

    # actions
    @action(
        'sync_ad_campaigns', 'Sync AdCampaigns for this AdAccount',
        'Sync AdCampaigns for this AdAccount', 'fa-rocket')
    def sync_ad_campaigns(self, items):
        """Call sync_ad_accounts."""

        if not isinstance(items, list):
            items = [items]

        for item in items:
            item.sync_ad_campaigns()

        return redirect('adcampaignview/list/')

    @action(
        'sync_all_ad_sets', 'Sync AdSets for this AdAccount',
        'Sync AdSets for this AdAccount', 'fa-rocket')
    def sync_all_ad_sets(self, items):
        """Call sync_all_ad_sets."""

        if not isinstance(items, list):
            items = [items]

        items[0].sync_all_ad_sets()

        return redirect('adsetview/list/')

    @action(
        'sync_all_ads', 'Sync Ads for this AdAccount',
        'Sync Ads for this AdAccount', 'fa-rocket')
    def sync_all_ads(self, items):
        """Call sync_all_ad_sets."""

        if not isinstance(items, list):
            items = [items]

        items[0].sync_all_ads()

        return redirect('adview/list/')

    @action(
        'sync_ads_insights', 'Sync Ads Insight for this AdAccount',
        'Sync Ads Insight this AdAccount', 'fa-rocket')
    def sync_ads_insights(self, items):
        """Call sync_ads_insights."""

        if not isinstance(items, list):
            items = [items]

        items[0].sync_ads_insights()

        return redirect('dailyadinsightsimpressiondeviceview/list/')


class AdCampaignView(SupersetModelView, DeleteMixin):
    """View For Facebook AdCampaign Model."""

    datamodel = SQLAInterface(AdCampaign)

    list_columns = [
        'ad_account.name', 'name', 'created_time'
    ]

    # actions
    @action(
        'sync_ad_sets', 'Sync AdSets for this AdCampaign',
        'Sync AdSets for this AdCampaign', 'fa-rocket')
    def sync_ad_sets(self, items):
        """Call sync_ad_sets."""

        if not isinstance(items, list):
            items = [items]

        for item in items:
            item.sync_ad_sets()

        return redirect('adcampaignview/list/')


class AdSetView(SupersetModelView, DeleteMixin):
    """View For Facebook AdSet Model."""

    datamodel = SQLAInterface(AdSet)

    list_columns = [
        'ad_campaign.ad_account.name', 'ad_campaign.name', 'name',
        'created_time'
    ]

    # actions
    @action(
        'sync_ads', 'Sync Ads for this AdSet',
        'Sync Ads for this AdSet', 'fa-rocket')
    def sync_ads(self, items):
        """Call sync_ad_sets."""

        if not isinstance(items, list):
            items = [items]

        for item in items:
            item.sync_ads()

        return redirect('adcampaignview/list/')

class AdView(SupersetModelView, DeleteMixin):
    """View For Facebook Ad Model."""

    datamodel = SQLAInterface(Ad)

    list_columns = [
        'ad_set.ad_campaign.ad_account.name',
        'ad_set.ad_campaign.name', 'ad_set.name', 'name',
        'created_time'
    ]

class DailyAdInsightsImpressionDeviceView(SupersetModelView, DeleteMixin):
    """View For Facebook DailyAdInsightsImpressionDevice Model."""

    datamodel = SQLAInterface(DailyAdInsightsImpressionDevice)

    list_columns = [
        'ad.name', 'date_stop', 'impression_device',
        'mobile_app_installs', 'cost_per_mobile_app_installs',
        'mobile_app_purchases', 'cost_per_mobile_app_purchases', 'cost',
    ]


# Register FacebookConnector Model View
appbuilder.add_view(
    FacebookConnectorView,
    'FacebookAds',
    icon='fa-facebook',
    category='Connectors',
    category_icon='fa-facebook',
    category_label=__('Connectors')
)


# Register AdAccount Model View
appbuilder.add_view(
    AdAccountView,
    'AdAccounts',
    icon='fa-facebook',
    category='Reports',
    category_icon='fa-table',
    category_label=__('Reports')
)


# Register AdCampaign Model View
appbuilder.add_view(
    AdCampaignView,
    'AdCampaigns',
    icon='fa-facebook',
    category='Reports',
    category_icon='fa-table',
    category_label=__('Reports')
)


# Register AdSet Model View
appbuilder.add_view(
    AdSetView,
    'AdSets',
    icon='fa-facebook',
    category='Reports',
    category_icon='fa-table',
    category_label=__('Reports')
)


# Register Ad Model View
appbuilder.add_view(
    AdView,
    'Ads',
    icon='fa-facebook',
    category='Reports',
    category_icon='fa-table',
    category_label=__('Reports')
)

# Register DailyAdInsightsImpressionDevice Model View
appbuilder.add_view(
    DailyAdInsightsImpressionDeviceView,
    'DailyAdInsightsImpressionDevices',
    icon='fa-facebook',
    category='Reports',
    category_icon='fa-table',
    category_label=__('Reports')
)
