# coding=utf-8
from __future__ import absolute_import, unicode_literals
from .performance import PerformanceReportDataSource
from adwords.adapters import GeoPerformanceReportAdapter


class GeoPerformanceReportDataSource(PerformanceReportDataSource):
    def __init__(self, storage, path):
        super(GeoPerformanceReportDataSource, self).__init__(
            storage=storage,
            path=path,
            name="GEO_PERFORMANCE_REPORT",
            adapters=(GeoPerformanceReportAdapter,)
        )
