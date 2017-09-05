# flask
from flask import redirect

# flask_appbuilder
from flask_appbuilder.fields import AJAXSelectField
from flask_appbuilder.fieldwidgets import (
    Select2AJAXWidget,
    Select2SlaveAJAXWidget
)
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.actions import action

# flask_babel
from flask_babel import gettext as __

# superset
from superset import appbuilder
from superset.views.base import SupersetModelView, DeleteMixin


# local
from .. models.ad import AdWordsConnector
from .. models.campaign import CampaignPerformanceReport




class CampaignPerformanceReportView(SupersetModelView, DeleteMixin):
    """View For AdWords CampaignPerformanceReport Model."""

    datamodel = SQLAInterface(CampaignPerformanceReport)

    list_columns = [
        'campaign_name', 'date', 'conversions',
        'cost', 'clicks', 'impression_device', 'impressions'
    ]

# Register AdWordsConnector Model View
appbuilder.add_view(
    CampaignPerformanceReportView,
    'CampaignPerformanceReport',
    icon='fa-google',
    category='Reports',
    category_icon='fa-google',
    category_label=__('Reports')
)
