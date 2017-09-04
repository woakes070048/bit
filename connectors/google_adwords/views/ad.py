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

class AdWordsConnectorView(SupersetModelView, DeleteMixin):
    """View For AdWords AdWordsConnector Model."""

    datamodel = SQLAInterface(AdWordsConnector)

    list_columns = [
        'name',
        'get_admin_data_sources'
    ]

    add_columns = [
        'name',
        'storage_path',
        'storage',
    ]

    edit_columns = add_columns

    add_form_extra_fields = {
        # 'storage': AJAXSelectField(
        #     'Storage',
        #     description='This will be populated with AJAX',
        #     datamodel=datamodel,
        #     col_name='storage',
        #     widget=Select2SlaveAJAXWidget(
        #         master_id='connector_id',
        #         endpoint='/googledrivestorageview/api/column/add/credentials?_flt_0_connector_id={{ID}}'
        #     )
        #     # widget=Select2AJAXWidget(
        #     #     endpoint='/googledrivestorageview/api/column/add/credentials'
        #     # )
        # ),
    }

    # actions
    @action(
        'sync_adwords_campaign_performance_report', 'Sync AdWords Campaign' \
        ' Performance Report for this AdAccount',
        'Sync AdWords Campaign Performance Report for this AdAccount',
        'fa-rocket'
    )
    def sync_adwords_campaign_performance_report(self, items):
        """Call sync_adwords_campaign_performance_report."""

        if not isinstance(items, list):
            items = [items]

        for item in items:
            item.sync_adwords_campaign_performance_report()

        return redirect('/')


# Register AdWordsConnector Model View
appbuilder.add_view(
    AdWordsConnectorView,
    'AdWords',
    icon='fa-google',
    category='Connectors',
    category_icon='fa-google',
    category_label=__('Connectors')
)


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
