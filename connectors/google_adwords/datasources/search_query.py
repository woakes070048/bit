# coding=utf-8
from __future__ import absolute_import, unicode_literals
from .performance import PerformanceReportDataSource
from adwords.adapters import SearchQueryPerformanceReportAdapter


class SearchQueryPerformanceReportDataSource(PerformanceReportDataSource):
    def __init__(self, storage, path):
        super(SearchQueryPerformanceReportDataSource, self).__init__(
            storage=storage,
            path=path,
            name="SEARCH_QUERY_PERFORMANCE_REPORT",
            adapters=(SearchQueryPerformanceReportAdapter,)
        )
