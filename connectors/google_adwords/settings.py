# GoogleAdWords Config File
from packaging.version import Version


CONNECTOR_INFO = {
    'version': Version('1.5'),

    'name': 'Google AdWords',

    'key': 'adwords',

    'static_folder': '/static/bit/images/connectors',

    'img_folder': 'img',

    'docs_folder': 'docs',

    'logo': 'logo.png',
    'logo_pat': '<img style="padding:15px;width:100px;float:left;" src="{}"/>',

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

    'reports': {
        'AD_PERFORMANCE_REPORT': {
            'name': 'Ad Performance Report',
            'key': 'AD_PERFORMANCE_REPORT',
        },
        'CAMPAIGN_PERFORMANCE_REPORT': {
            'name': 'Campaign Performance Report',
            'key': 'CAMPAIGN_PERFORMANCE_REPORT',
        },
        'GENDER_PERFORMANCE_REPORT': {
            'name': 'Gender Performance Report',
            'key': 'GENDER_PERFORMANCE_REPORT',
        },
        'GEO_PERFORMANCE_REPORT': {
            'name': 'Geo Performance Report',
            'key': 'GEO_PERFORMANCE_REPORT',
        },
        'PLACEHOLDER_FEED_ITEM_REPORT': {
            'name': 'Placeholder Feed Item Report',
            'key': 'PLACEHOLDER_FEED_ITEM_REPORT',
        },
        'PLACEMENT_PERFORMANCE_REPORT': {
            'name': 'Placement Performance Report',
            'key': 'PLACEMENT_PERFORMANCE_REPORT',
        },
        'SEARCH_QUERY_PERFORMANCE_REPORT': {
            'name': 'Search Query Performance Report',
            'key': 'SEARCH_QUERY_PERFORMANCE_REPORT',
        },
    },

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

        'CampaignId': 'String',
        'CampaignName': 'String',
        'CityCriteriaId': 'String',
        'Clicks': 'Integer',
        'Conversions': 'Numeric',
        'Cost': 'Numeric',
        'CountryCriteriaId': 'String',
        'Criteria': 'String',
        'Date': 'DateTime',
        'Device': 'String',
        'FeedId': 'String',
        'FeedItemId': 'String',
        'GeoTargetingCriterionId': 'String',
        'GeoTargetingRestriction': 'String',
        'Id': 'String',
        'Impressions': 'Integer',
        'IsTargetingLocation': 'Boolean',
        'KeywordId': 'String',
        'KeywordTextMatchingQuery': 'String',
        'LocationType': 'String',
        'MetroCriteriaId': 'String',
        'QueryMatchTypeWithVariant': 'String',
    },

    'replace_values': {
        # replace values by field name
        # and key-value pair

        # 'Media Source': {
        #     'Facebook Ads': 'facebook',
        #     'googleadwords_int': 'adwords',
        # },
    },

    'replace_in_values': {
        # replace in values by field name
        # and key-value pair

        'Cost': [',', ''],
        'Conversions': [',', ''],
    },
}
