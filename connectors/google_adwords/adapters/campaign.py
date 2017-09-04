# local
from .performance import AdwordsPerformanceReportAdapter


class CampaignPerformanceReportAdapter(AdwordsPerformanceReportAdapter):
    """
    Data Adapter For Campaign Performance Report 
    https://developers.google.com/adwords/api/docs/appendix/reports
    /campaign-performance-report 
    """

    def __init__(self, data):
        super(CampaignPerformanceReportAdapter, self).__init__(
            data=data,
            name='campaign'
        )

    @property
    def breakdowns(self):
        return dict(device=self.device)
