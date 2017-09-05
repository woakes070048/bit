# flask_appbuilder
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

# flask_babel
from flask_babel import gettext as __

# superset
from superset import appbuilder
from superset.views.base import SupersetModelView, DeleteMixin, BaseSupersetView

# locale
from bit.models import Connector


# for show all Connectors in system
class ConnectorView(SupersetModelView, DeleteMixin):
    """View For Connector Model."""

    datamodel = SQLAInterface(Connector)

    list_columns = [
        'name', 'connector_info', 'admin_data_sources'
        # 'admin_data_sources'
    ]

    add_columns = []


# Register ConnectorView Model View
appbuilder.add_view(
    ConnectorView,
    'Connections',
    # href='/connections',
    icon='fa-random',
    category='Connectors',
    category_icon='fa-random',
    category_label=__('Connectors')
)
#
# class MyView(BaseSupersetView):
#
#     default_view = 'method1'
#
#     @expose('/method1/')
#     @has_access
#     def method1(self):
#         # do something with param1
#         # and return to previous page or index
#         return self.render_template('bit/table_preview.html')
#
#     @expose('/method2/<string:param1>')
#     @has_access
#     def method2(self, param1):
#         # do something with param1
#         # and render template with param
#         param1 = 'Goodbye %s' % (param1)
#         return param1

# appbuilder.add_view(MyView, "Method1", category='Connectors')
# appbuilder.add_link("Method2", href='/etl/add/AppsFlyer', category='Connectors')

# appbuilder.add_view_no_menu(MyView())
# appbuilder.add_link("Method2", href='/myview/method2/john', category='My View')

