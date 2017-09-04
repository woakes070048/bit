# local
from .performance import AdwordsPerformanceReportAdapter


class PlacementPerformanceReportAdapter(AdwordsPerformanceReportAdapter):
    """
    Data Adapter For Placement Performance Report
    https://developers.google.com/adwords/api/docs/appendix/reports
    /placement-performance-report
    """

    def __init__(self, data):
        super(PlacementPerformanceReportAdapter, self).__init__(
            data=data,
            name='placement'
        )

    @property
    def breakdowns(self):
        return dict(
            device=self.device,
            placement=self.data['Criteria'],
        )
