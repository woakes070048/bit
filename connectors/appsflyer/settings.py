# AppsFlyer Config File
from packaging.version import Version


CONNECTOR_INFO = {
    'version': Version('1.0'),

    'name': 'AppsFlyer',

    'key': 'appsflyer',

    'img_folder': 'img',

    'docs_folder': 'docs',

    'logo': 'logo.png',

    'description': 'Lorem Ipsum is simply dummy text of the printing and'
                   ' typesetting industry. Lorem Ipsum has been the'
                   ' industry\'s standard dummy text ever since the 1500s,'
                   ' when an unknown printer took a galley of type and'
                   ' scrambled it to make a type specimen book. It has'
                   ' survived not only five <b>centuries</b>, but also the'
                   ' leap into electronic typesetting, remaining essentially'
                   ' unchanged. It was popularised in the 1960s with the'
                   ' release of Letraset sheets containing Lorem Ipsum'
                   ' passages, and more recently with desktop publishing'
                   ' software like Aldus PageMaker including versions of'
                   ' Lorem Ipsum.',

    'report_cache_timeout': 60 * 60 * 24,

    'sync_field': 'date',

    'reports': frozenset([
        'installs_report',
        'in_app_events_report',
        'partners_report',
        'geo_report',
        'partners_by_date_report',
        'geo_by_date_report'
    ]),

    'fields_types': {
        """ 
            db SQLAlchemy Data Types
            http://docs.sqlalchemy.org/en/latest/core/type_basics.html
        
            basic:
            String
            Text
            Integer
            Numeric
            Boolean
            DateTime (timezone=False)
        """

        'Ad': 'String',
        'Ad ID': 'String',
        'Ad Type': 'String',
        'Adset': 'String',
        'Adset ID': 'String',
        'Advertising ID': 'String',
        'af_purchase (Event counter)': 'Numeric',
        'af_purchase (Sales in USD)': 'Numeric',
        'af_purchase (Unique users)': 'Integer',
        'Agency/PMD (af_prt)': 'String',
        'Android ID': 'String',
        'App ID': 'String',
        'App Name': 'String',
        'App Version': 'String',
        'AppsFlyer ID': 'String',
        'ARPU': 'Numeric',
        'Attributed Touch Time': 'DateTime',
        'Attributed Touch Type': 'String',
        'Attribution Lookback': 'String',
        'Average eCPI': 'Numeric',
        'Bundle ID': 'String',
        'Campaign': 'String',
        'Campaign (c)': 'String',
        'Campaign ID': 'String',
        'Carrier': 'String',
        'Channel': 'String',
        'City': 'String',
        'Clicks': 'Integer',
        'Contributor 1 Campaign': 'String',
        'Contributor 1 Media Source': 'String',
        'Contributor 1 Partner': 'String',
        'Contributor 1 Touch Time': 'DateTime',
        'Contributor 1 Touch Type': 'String',
        'Contributor 2 Campaign': 'String',
        'Contributor 2 Media Source': 'String',
        'Contributor 2 Partner': 'String',
        'Contributor 2 Touch Time': 'DateTime',
        'Contributor 2 Touch Type': 'String',
        'Contributor 3 Campaign': 'String',
        'Contributor 3 Media Source': 'String',
        'Contributor 3 Partner': 'String',
        'Contributor 3 Touch Time': 'DateTime',
        'Contributor 3 Touch Type': 'String',
        'Conversion Rate': 'Numeric',
        'Cost Currency': 'String',
        'Cost Model': 'String',
        'Cost Value': 'Numeric',
        'Country': 'String',
        'Country Code': 'String',
        'CTR': 'Numeric',
        'Customer User ID': 'String',
        'Date': 'DateTime',
        'Device Type': 'String',
        'DMA': 'Integer',
        'Event Name': 'String',
        'Event Revenue': 'Numeric',
        'Event Revenue Currency': 'String',
        'Event Revenue USD': 'Numeric',
        'Event Source': 'String',
        'Event Time': 'DateTime',
        'Event Value': 'HSTORE',
        'first_open (Event counter)': 'Integer',
        'first_open (Sales in USD)': 'Integer',
        'first_open (Unique users)': 'Integer',
        'HTTP Referrer': 'String',
        'IDFA': 'String',
        'IDFV': 'String',
        'IMEI': 'String',
        'Impressions': 'Integer',
        'Install Time': 'DateTime',
        'Installs': 'Integer',
        'IP': 'String',
        'Is Primary Attribution': 'Boolean',
        'Is Receipt Validated': 'Boolean',
        'Is Retargeting': 'Boolean',
        'Keywords': 'String',
        'Language': 'String',
        'Loyal Users': 'Integer',
        'Loyal Users/Installs': 'Numeric',
        'Media Source': 'String',
        'Media Source (pid)': 'String',
        'Operator': 'String',
        'Original URL': 'String',
        'OS Version': 'String',
        'Partner': 'String',
        'Platform': 'String',
        'Postal Code': 'String',
        'Reengagement Window': 'String',
        'Region': 'String',
        'Retargeting Conversion Type': 'String',
        'ROI': 'Numeric',
        'SDK Version': 'String',
        'session_start (Event counter)': 'Integer',
        'session_start (Sales in USD)': 'Integer',
        'session_start (Unique users)': 'Integer',
        'Sessions': 'Integer',
        'Site ID': 'String',
        'State': 'String',
        'Sub Param 1': 'String',
        'Sub Param 2': 'String',
        'Sub Param 3': 'String',
        'Sub Param 4': 'String',
        'Sub Param 5': 'String',
        'Sub Site ID': 'String',
        'Total Cost': 'Numeric',
        'Total Revenue': 'Numeric',
        'User Agent': 'String',
        'WIFI': 'Boolean',
    }
}
