# GoogleAdWords Config File
from packaging.version import Version


CONNECTOR_INFO = {
    'version': Version('1.0'),

    'name': 'Google AdWords',

    'key': 'adwords',

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
        'CAMPAIGN_PERFORMANCE_REPORT',
        'GENDER_PERFORMANCE_REPORT',
        'GEO_PERFORMANCE_REPORT',
        'PLACEHOLDER_FEED_ITEM_REPORT',
        'PLACEMENT_PERFORMANCE_REPORT',
        'SEARCH_QUERY_PERFORMANCE_REPORT'
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
    }
}
