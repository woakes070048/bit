# Facebook Ads Config File
from packaging.version import Version

from facebook_business.adobjects.adsinsights import AdsInsights as fbAdsInsights

from superset import app


config = app.config

DB_PREFIX = '{}'.format(
    config.get('APP_DB_PREFIX', 'bit'),
)
CONNECTOR_KEY = 'facebook'  # rename to facebook_ads and migrate db tables

CONNECTOR_INFO = {

    'version': Version('1.5'),

    'table_prefix': '{}_{}'.format(
        DB_PREFIX,
        CONNECTOR_KEY,
    ),

    'app_id': config.get('FB_APP_ID', 'FB_APP_ID'),
    'app_secret': config.get('FB_APP_SECRET', 'FB_APP_SECRET'),

    'name': 'Facebook ADS',
    'key': CONNECTOR_KEY,

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

    'sync_field': 'date',

    'reports': {
        'conversion_device': {
            'name': 'Conversion Device',
            'action_breakdowns': [
                fbAdsInsights.ActionBreakdowns.action_device,
                fbAdsInsights.ActionBreakdowns.action_type
            ],
        },
        'age': {
            'name': 'Age',
            'breakdowns': [fbAdsInsights.Breakdowns.age],
        },
        'gender': {
            'name': 'Gender',
            'breakdowns': [fbAdsInsights.Breakdowns.gender],
        },
        'age_gender': {
            'name': 'Age and Gender',
            'breakdowns': [
                fbAdsInsights.Breakdowns.age,
                fbAdsInsights.Breakdowns.gender
            ],
        },
        'country': {
            'name': 'Country',
            'breakdowns': [fbAdsInsights.Breakdowns.country],
        },
        'region': {
            'name': 'Region',
            'breakdowns': [fbAdsInsights.Breakdowns.region],
        },
        'dma_region': {
            'name': 'DMA Region',
            'breakdowns': [fbAdsInsights.Breakdowns.dma],
        },
        'impression_device': {
            'name': 'Impression Device',
            'breakdowns': [fbAdsInsights.Breakdowns.impression_device],
        },
        'platform': {
            'name': 'Platform',
            'breakdowns': [fbAdsInsights.Breakdowns.publisher_platform],
        },
        'platform_device': {
            'name': 'Platform and Device',
            'breakdowns': [
                fbAdsInsights.Breakdowns.publisher_platform,
                fbAdsInsights.Breakdowns.impression_device
            ],
        },
        'placement': {
            'name': 'Placement',
            'breakdowns': [
                fbAdsInsights.Breakdowns.publisher_platform,
                fbAdsInsights.Breakdowns.platform_position,
                fbAdsInsights.Breakdowns.device_platform
            ],
        },
        'placement_device': {
            'name': 'Placement and Device',
            'breakdowns': [
                fbAdsInsights.Breakdowns.publisher_platform,
                fbAdsInsights.Breakdowns.platform_position,
                fbAdsInsights.Breakdowns.device_platform,
                fbAdsInsights.Breakdowns.impression_device
            ],
        },
        'product_id': {
            'name': 'Product ID',
            'breakdowns': [fbAdsInsights.Breakdowns.product_id],
        },
    },
}
