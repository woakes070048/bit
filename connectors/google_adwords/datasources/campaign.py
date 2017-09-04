# coding=utf-8
from __future__ import absolute_import, unicode_literals
from .performance import PerformanceReportDataSource
from .. adapters import CampaignPerformanceReportAdapter
from .. models.campaign import CampaignPerformanceReport


class CampaignPerformanceReportDataSource(PerformanceReportDataSource):
    """
    Data Source For Campaign Performance Report 
    https://developers.google.com/adwords/api/docs/appendix/reports
    /campaign-performance-report 
    """

    def __init__(self, storage, path):
        super(CampaignPerformanceReportDataSource, self).__init__(
            storage=storage,
            path=path,
            name='CAMPAIGN_PERFORMANCE_REPORT',
            adapters=(CampaignPerformanceReportAdapter,),
            models=(CampaignPerformanceReport,),
        )
