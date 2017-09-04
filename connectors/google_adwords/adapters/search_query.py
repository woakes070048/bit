# local
from .performance import AdwordsPerformanceReportAdapter


class SearchQueryPerformanceReportAdapter(AdwordsPerformanceReportAdapter):
    """
    Data Adapter For  Search Query Performance Report
    https://developers.google.com/adwords/api/docs/appendix/reports
    /search-query-performance-report
    """

    def __init__(self, data):
        super(SearchQueryPerformanceReportAdapter, self).__init__(
            data=data,
            name='search_query'
        )

    @property
    def breakdowns(self):
        return dict(
            device=self.device,
            keyword_id=self.data['KeywordId'],
            keyword_text_matching_query=self.data['KeywordTextMatchingQuery'],
            query_match_type_with_variant=self.data['QueryMatchTypeWithVariant']
        )
