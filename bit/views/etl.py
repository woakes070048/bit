"""Views used by the ETL MODEL"""
# system
import logging
from datetime import datetime, timedelta

# sqlalchemy
import sqlalchemy as sa
from flask_appbuilder.fields import AJAXSelectField
from sqlalchemy.dialects.postgresql import HSTORE

# flask
from flask import redirect

# flask_babel
from flask_babel import lazy_gettext as _
from flask_babel import gettext as __

# flask_appbuilder
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.actions import action
from flask_appbuilder.fieldwidgets import (
    BS3TextFieldWidget,
    Select2SlaveAJAXWidget,
    Select2AJAXWidget
)
from flask_appbuilder.fieldwidgets import Select2Widget

# wtforms
from wtforms import StringField
from wtforms import SelectField

# superset
from superset import db
from superset import appbuilder
from superset.views.base import SupersetModelView
from superset.views.base import DeleteMixin
from superset.views.base import get_datasource_exist_error_mgs
from superset.connectors.sqla.views import TableModelView
from superset.connectors.sqla.views import TableColumnInlineView

# local bit package
from bit.models.etl import EtlPeriod
from bit.models.etl import EtlTable
from bit.models.connector import Connector
from bit.models.performance_report import PerformanceReport
from bit.models.datasource import DataSourceInfo


def get_etl_table_exist_error_mgs(full_name):
    return __("Etl table %(name)s already exists", name=full_name)


class BS3TextFieldROWidget(BS3TextFieldWidget):
    def __call__(self, field, **kwargs):
        kwargs['readonly'] = 'true'
        return super(BS3TextFieldROWidget, self).__call__(field, **kwargs)


class EtlTableView(SupersetModelView, DeleteMixin):
    """View For EtlTable Model."""

    datamodel = SQLAInterface(EtlTable)

    list_columns = [
        'connector', 'table.database', 'table', 'datasource', 'sql_table_name',
        'sync_field', 'sync_last', 'sync_last_time',
        'progress', 'status', 'repr_sync_periodic', 'sync_next_time',
        'is_valid', 'is_active', 'is_scheduled'
        # 'table.sql'
    ]

    add_columns = [
        'connector', 'table', 'datasource', 'name', 'sync_field', 'sync_last', 'chunk_size',
        'sync_periodic', 'sync_periodic_hour'
    ]

    edit_schema = ['schema']

    edit_columns = [
        'sync_field', 'chunk_size', 'sync_periodic', 'sync_periodic_hour',
        'is_active'
    ]

    edit_columns = edit_columns
    # edit_columns = add_columns + ['sync_last_time', 'sync_next_time']

    label_columns = {
        'table.database': 'Instance',
        'connector': 'DataSource Connector',
        'table': 'DataSource SQLTable',
        'name': '_etl_{name}',
    }

    description_columns = {
        'table': _(
            '<a href="/tablemodelview/list/">Create table </a>'
        ),
    }

    etl_extra_fields = {

        # 'datasource': AJAXSelectField('Extra Field2',
        #     description='Extra Field description',
        #     datamodel=datamodel,
        #     col_name='datasource',
        #     widget=Select2AJAXWidget(
        #         # master_id='connector',
        #         endpoint='/connectorview/api/column/add/datasource'
        #
        #         # http://127.0.0.1:5000/connectorview/api/column/add/get_admin_data_sources?_flt_0_id=1
        #         # endpoint='/appsflyerconnectorview/api/column/add/contact_sub_group?_flt_0__id={{ID}}'
        #
        #         # endpoint='/appsflyerconnectorview/api/read?_flt_0_id={{ID}}'
        #     )
        # ),


        # 'datasource': AJAXSelectField('Extra Field2',
        #     description='Extra Field description',
        #     datamodel=datamodel,
        #     col_name='reports',
        #     widget=Select2SlaveAJAXWidget(
        #         master_id='connector',
        #         # endpoint='/appsflyerconnectorview/api/column/add/contact_sub_group?_flt_0__id={{ID}}')
        #         endpoint='/appsflyerconnectorview/api/read?_flt_0_id={{ID}}'
        #     )
        # ),
        'sync_periodic': SelectField(
            choices=EtlPeriod.CHOICES,
            widget=Select2Widget(),
            coerce=int
        ),
        'sync_periodic_hour': SelectField(
            choices=EtlPeriod.HOURS,
            widget=Select2Widget(),
            coerce=int,
            description=_(
                'Use if you select one of [Once a month, '
                'Once a week, Once a day] Sync Periodic'
            )
        ),
    }

    add_form_extra_fields = etl_extra_fields
    edit_form_extra_fields = etl_extra_fields

    description_columns = {
        # 'sync_periodic_hour': _(
        #     'Use if you select one of [Once a month, '
        #     'Once a week, Once a day] Periodic'
        # ),
    }

    # etl_extra_fields = {'schema': StringField(widget=BS3TextFieldROWidget())}
    # add_form_extra_fields = etl_extra_fields
    # edit_form_extra_fields = etl_extra_fields
    # related_views = [TableColumnInlineView]

    # actions
    @action('sync_etl', 'sync',
            'Sync data for this table', 'fa-play')
    def sync(self, item):
        """Call sync etl."""
        item[0].sync()

        return redirect('etltableview/list/')

    @action('sync_etl_stop', 'sync stop',
            'Stop sync data for this table', 'fa-stop')
    def sync_stop(self, item):
        """Call stop etl."""
        item[0].stop()

        return redirect('etltableview/list/')

    @action('sync_etl_once', 'sync once',
            'Sync data for this table', 'fa-step-forward')
    def sync_once(self, item):
        """Call test_sync_etl."""
        item[0].sync_once()

        return redirect('etltableview/list/')

    def pre_add(self, obj):
        """Check data before save"""

        if obj.name == '':
            raise Exception('Enter a table name')

        # if obj.table_id:
        #     # Create table
        obj.create_table()
        obj.sync_next_time = obj.get_next_sync()

    def pre_update(self, obj):
        obj.sync_next_time = obj.get_next_sync()

    def pre_delete(self, obj):
        logging.info('pre_delete')

        if obj.exist_table():
            obj.delete_table()

    # def _delete(self, pk):
    #     DeleteMixin._delete(self, pk)


# Register EtlTableView Model View
appbuilder.add_view(
    EtlTableView,
    'Tables',
    icon='fa-table',
    category='ETL',
    category_icon='fa-refresh',
    category_label=__('ETL')
)
# for show all Reports in system


class PostgreSQLAInterface(SQLAInterface):
    def is_text(self, col_name):
        try:
            return (
                isinstance(self.list_columns[col_name].type, sa.types.String)
                or isinstance(self.list_columns[col_name].type, HSTORE)
            )
        except Exception:
            return False


class PerformanceReportView(SupersetModelView, DeleteMixin):
    """View For Connector Model."""

    datamodel = PostgreSQLAInterface(PerformanceReport)

    list_columns = [
        'campaign_source',
        'campaign_name',
        'date',
        'breakdowns',
        'clicks_unique',
        'impressions',
        'cost',
    ]


# Register PerformanceReportView Model View
appbuilder.add_view(
    PerformanceReportView,
    'PerformanceReports',
    icon='fa-table',
    category='Reports',
    category_icon='fa-table',
    category_label=__('Reports')
)

class DataSourceInfoView(SupersetModelView, DeleteMixin):
    """View For Connector Model."""

    datamodel = SQLAInterface(DataSourceInfo)

    list_columns = [
        'source',
        'name',
        'sync_time',
        'last_id',
    ]


# Register DataSourceInfoView Model View
appbuilder.add_view(
    DataSourceInfoView,
    'DataSourceInfo',
    icon='fa-table',
    category='ETL',
    category_icon='fa-refresh',
    category_label=__('ETL')
)


#
# class EtlTableColumnInlineViewttt(SupersetModelView):
#     datamodel = SQLAInterface(EtlTableColumn)
#     # list_columns = ['column_name', 'verbose_name']
#     # list_widget = ListBlock
#
#
# class EtlTableColumnInlineView(CompactCRUDMixin, SupersetModelView):  # noqa
#     datamodel = SQLAInterface(EtlTableColumn)
#     can_delete = False
#     list_widget = ListWidgetWithCheckboxes
#     edit_columns = [
#         'column_name', 'verbose_name', 'description',
#         'type', 'groupby', 'filterable',
#         'etl_table', 'count_distinct', 'sum', 'min', 'max', 'expression',
#         'is_dttm', 'python_date_format', 'database_expression']
#     add_columns = edit_columns
#     list_columns = ['is_dttm']
#     # list_columns = [
#     #     'column_name', 'type', 'groupby', 'filterable', 'count_distinct',
#     #     'sum', 'min', 'max', 'is_dttm']
#     page_size = 500
#     description_columns = {
#         'is_dttm': _(
#             "Whether to make this column available as a "
#             "[Time Granularity] option, column has to be DATETIME or "
#             "DATETIME-like"),
#         'filterable': _(
#             "Whether this column is exposed in the `Filters` section "
#             "of the explore view."),
#         'type': _(
#             "The data type that was inferred by the database. "
#             "It may be necessary to input a type manually for "
#             "expression-defined columns in some cases. In most case "
#             "users should not need to alter this."),
#         'expression': utils.markdown(
#             "a valid SQL expression as supported by the underlying backend. "
#             "Example: `substr(name, 1, 1)`", True),
#         'python_date_format': utils.markdown(Markup(
#             "The pattern of timestamp format, use "
#             "<a href='https://docs.python.org/2/library/"
#             "datetime.html#strftime-strptime-behavior'>"
#             "python datetime string pattern</a> "
#             "expression. If time is stored in epoch "
#             "format, put `epoch_s` or `epoch_ms`. Leave `Database Expression` "
#             "below empty if timestamp is stored in "
#             "String or Integer(epoch) type"), True),
#         'database_expression': utils.markdown(
#             "The database expression to cast internal datetime "
#             "constants to database date/timestamp type according to the DBAPI. "
#             "The expression should follow the pattern of "
#             "%Y-%m-%d %H:%M:%S, based on different DBAPI. "
#             "The string should be a python string formatter \n"
#             "`Ex: TO_DATE('{}', 'YYYY-MM-DD HH24:MI:SS')` for Oracle"
#             "Superset uses default expression based on DB URI if this "
#             "field is blank.", True),
#     }
#     label_columns = {
#         'column_name': _("Column"),
#         'verbose_name': _("Verbose Name"),
#         'description': _("Description"),
#         'groupby': _("Groupable"),
#         'filterable': _("Filterable"),
#         'etl_table': _("Etl Table"),
#         'count_distinct': _("Count Distinct"),
#         'sum': _("Sum"),
#         'min': _("Min"),
#         'max': _("Max"),
#         'expression': _("Expression"),
#         'is_dttm': _("Is temporal"),
#         'python_date_format': _("Datetime Format"),
#         'database_expression': _("Database Expression")
#     }
# appbuilder.add_view_no_menu(EtlTableColumnInlineView)
#
# class EtlTableView(SupersetModelView, DeleteMixin):
#     """View For EtlTable Model."""
#
#     datamodel = SQLAInterface(EtlTable)
#
#     add_columns = ['database', 'schema', 'table_name']
#
#     edit_columns = [
#         'table_name', 'filter_select_enabled', 'slices',
#         'database', 'schema',
#         'description', 'owner',
#         'default_endpoint', 'offset', 'cache_timeout']
#
#     show_columns = edit_columns + ['perm']
#
#     # related_views = [EtlTableColumnInlineView, SqlMetricInlineView]
#     related_views = [EtlTableColumnInlineView]
#
#
# # Register EtlTableView Model View
# appbuilder.add_view(
#     EtlTableView,
#     'Tables',
#     icon='fa-table',
#     category='ETL',
#     category_icon='fa-bicycle',
#     category_label=__('ETL')
# )
