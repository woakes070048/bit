# local
from .performance import AdwordsPerformanceReportAdapter


class GenderPerformanceReportAdapter(AdwordsPerformanceReportAdapter):
    """
    Data Adapter For Gender Performance Report
    https://developers.google.com/adwords/api/docs/appendix/reports
    /gender-performance-report 
    """

    def __init__(self, data):
        super(GenderPerformanceReportAdapter, self).__init__(
            data=data,
            name="gender"
        )

    @property
    def breakdowns(self):
        return dict(
            device=self.device,
            gender=self.data['Criteria']
        )
