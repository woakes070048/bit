# system
import logging
import httplib2
import json

# flask
from flask import redirect

# flask_babel
from flask_babel import gettext as __

# flask_appbuilder
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.actions import action

# superset
from superset import appbuilder
from superset.views.base import SupersetModelView, DeleteMixin

# local
from .. models.connector import FacebookConnector
from .. settings import CONNECTOR_INFO as CI

class FacebookConnectorView(SupersetModelView, DeleteMixin):
    """View For Facebook FacebookConnector Model."""

    datamodel = SQLAInterface(FacebookConnector)

    list_columns = ['name', 'uid', 'admin_data_sources']

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
                      APP_ID=CI.get('app_id'),
                      APP_SECRET=CI.get('app_secret'),
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


# Register FacebookConnector Model View
appbuilder.add_view(
    FacebookConnectorView,
    'FacebookAds',
    icon='fa-facebook',
    category='Connectors',
    category_icon='fa-facebook',
    category_label=__('Connectors')
)