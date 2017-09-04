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
from .. models.google_drive_storage import GoogleDriveStorage

class GoogleDriveStorageView(SupersetModelView, DeleteMixin):
    """View For Facebook FacebookConnector Model."""

    datamodel = SQLAInterface(GoogleDriveStorage)


# Register GoogleDriveStorageView Model View
appbuilder.add_view(
    GoogleDriveStorageView,
    'GoogleDriveStorage',
    icon='fa-google',
    category='Connectors',
    category_icon='fa-google',
    category_label=__('Connectors')
)
