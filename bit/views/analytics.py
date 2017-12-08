# flask_appbuilder
from flask_appbuilder.models.sqla.interface import SQLAInterface

# flask_babel
from flask_babel import gettext as __

# superset
from superset import appbuilder
from superset.views.base import SupersetModelView
from superset.views.base import DeleteMixin

# locale
from bit.models import Identify


class IdentifyView(SupersetModelView, DeleteMixin):
    """View For Analytics Identify Model."""

    datamodel = SQLAInterface(Identify)


# Register ConnectorView Model View
appbuilder.add_view(
    IdentifyView,
    'identifys',
    # href='/connections',
    icon='fa-random',
    category='Identify',
    category_icon='fa-random',
    category_label=__('Identify')
)
