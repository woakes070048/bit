# -*- coding: utf-8 -*-
from __future__ import absolute_import

# flask_appbuilder
from flask_appbuilder.models.sqla.interface import SQLAInterface

# flask_babel
from flask_babel import gettext as __

# superset
from superset import appbuilder
from superset.views.base import SupersetModelView, DeleteMixin

# local
from .models import Connector, BitPackages


class ConnectorView(SupersetModelView, DeleteMixin):
    """View For Connector Model."""

    datamodel = SQLAInterface(Connector)


class BitPackagesModelView(SupersetModelView, DeleteMixin):
    """
        View For BitPackages Model.

        TODO:
        get list of exist connectors from installed
        and from pypi packages
        if package (connector) installed user can use.
        in model we save connector name and folder to connector
    """

    datamodel = SQLAInterface(BitPackages)

    list_columns = ['id']


# Register Connector Model View
appbuilder.add_view(
    ConnectorView,
    name='BIT Connectors',
    label=__('BIT Connectors'),
    icon='fa-cube',
    category='Sources',
    category_label=__('Sources')
)


# Register BitPackages Model View
appbuilder.add_view(
    BitPackagesModelView,
    name='BIT Packages',
    label=__('BIT Packages'),
    icon='fa-cube',
    category='Sources',
    category_label=__('Sources')
)
