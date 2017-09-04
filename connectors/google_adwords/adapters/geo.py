# local
from .performance import AdwordsPerformanceReportAdapter


class GeoPerformanceReportAdapter(AdwordsPerformanceReportAdapter):
    """
    Data Adapter For Geo Performance Report
    https://developers.google.com/adwords/api/docs/appendix/reports
    /geo-performance-report 
    """

    def __init__(self, data):
        super(GeoPerformanceReportAdapter, self).__init__(
            data=data,
            name='geo'
        )

    @property
    def breakdowns(self):
        return dict(
            device=self.device,
            country_criteria_id=self.data['CountryCriteriaId'],
            city_criteria_id=self.data['CityCriteriaId'],
            is_targeting_location=self.data['IsTargetingLocation'],
            location_type=self.data['LocationType'],
            metro_criteria_id=self.data['MetroCriteriaId']
        )
