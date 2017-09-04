# werkzeug
from werkzeug.utils import redirect

# flask_appbuilder
from flask_appbuilder import action
from flask_appbuilder.models.sqla.interface import SQLAInterface

# flask_babel
from flask_babel import gettext as __

# superset
from superset import appbuilder
from superset.views.base import SupersetModelView, DeleteMixin

# local
from .. models.connector import AppsFlyerConnector


# for show all Connectors in system
class AppsFlyerConnectorView(SupersetModelView, DeleteMixin):
    """View For Connector Model."""

    datamodel = SQLAInterface(AppsFlyerConnector)

    list_columns = [
        'name', 'app_id', 'get_admin_data_sources'
    ]

    add_columns = [
        'name', 'app_id', 'api_token', 'url_pat'
    ]

    edit_columns = add_columns

    @action(
        'web_test', 'web_test',
        'web_test', 'fa-rocket')
    def web_test(self, items):
        if not isinstance(items, list):
            items = [items]
        items[0].web_test()
        return redirect('appsflyerconnectorview/list/')

# Register ConnectorView Model View
appbuilder.add_view(
    AppsFlyerConnectorView,
    'AppsFlyer',
    icon='fa-random',
    category='Connectors',
    category_icon='fa-rocket',
    category_label=__('Connectors')
)
