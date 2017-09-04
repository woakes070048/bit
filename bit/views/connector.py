from flask_appbuilder.models.sqla.interface import SQLAInterface

# flask_babel
from flask_babel import lazy_gettext as _
from flask_babel import gettext as __

from superset import appbuilder
from superset.views.base import SupersetModelView, DeleteMixin

from bit.models import Connector


# for show all Connectors in system
class ConnectorView(SupersetModelView, DeleteMixin):
    """View For Connector Model."""

    datamodel = SQLAInterface(Connector)

    list_columns = [
        'type', 'name', 'get_admin_data_sources'
    ]

    add_columns = []


# Register ConnectorView Model View
appbuilder.add_view(
    ConnectorView,
    'Connections',
    icon='fa-random',
    category='Connectors',
    category_icon='fa-random',
    category_label=__('Connectors')
)
