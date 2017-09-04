# local
from .performance import AdwordsPerformanceReportAdapter


class PlaceHolderPerformanceReportAdapter(AdwordsPerformanceReportAdapter):
    """
    Data Adapter For Gender Performance Report
    https://developers.google.com/adwords/api/docs/appendix/reports/
    placeholder-report
    """

    def __init__(self, data):
        super(PlaceHolderPerformanceReportAdapter, self).__init__(
            data=data,
            name='placeholder'
        )

    @property
    def breakdowns(self):
        return dict(
            device=self.device,
            criteria=self.data['Criteria'],
            feed_id=self.data['FeedId'],
            feed_item_id=self.data['FeedItemId'],
            geo_targeting_criterion_id=self.data['GeoTargetingCriterionId'],
            geo_targeting_restriction=self.data['GeoTargetingRestriction'],
        )
