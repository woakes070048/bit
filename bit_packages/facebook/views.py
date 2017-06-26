# -*- coding: utf-8 -*-
from __future__ import absolute_import

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
from .models import FacebookConnector
from .models import AdAccount
from .models import AdCampaign


class FacebookConnectorView(SupersetModelView, DeleteMixin):
    """View For Facebook FacebookConnector Model."""

    datamodel = SQLAInterface(FacebookConnector)

    list_columns = ['name', 'uid', 'access_token']

    # add_template = 'bit_packages/facebook/templates/add_connector.html'
    add_template = 'facebook/add_connector.html'

    add_columns = ['name', 'uid', 'access_token']

    edit_columns = add_columns

    # actions
    @action('sync_ad_accounts', 'Sync AdAccounts for this connector',
            'Sync AdAccounts for this connector', 'fa-rocket')
    def sync_ad_accounts(self, item):
        """Call sync_ad_accounts."""
        item[0].sync_ad_accounts()

        return redirect(self.get_redirect())


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

        return redirect(self.get_redirect())


class AdCampaignView(SupersetModelView, DeleteMixin):
    """View For Facebook AdCampaign Model."""

    datamodel = SQLAInterface(AdCampaign)

    list_columns = [
        'ad_account', 'name'
    ]


# Register FacebookConnector Model View
appbuilder.add_view(
    FacebookConnectorView,
    'Connectors',
    icon='fa-facebook-official',
    category='Facebook',
    category_icon='fa-facebook-official',
    category_label=__('Facebook')
)


# Register AdAccount Model View
appbuilder.add_view(
    AdAccountView,
    'AdAccounts',
    icon='fa-facebook-official',
    category='Facebook',
    category_icon='fa-facebook-official',
    category_label=__('Facebook')
)


# Register AdCampaign Model View
appbuilder.add_view(
    AdCampaignView,
    'AdCampaigns',
    icon='fa-facebook-official',
    category='Facebook',
    category_icon='fa-facebook-official',
    category_label=__('Facebook')
)
