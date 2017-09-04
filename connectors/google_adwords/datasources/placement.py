# coding=utf-8
from __future__ import absolute_import, unicode_literals
from .performance import PerformanceReportDataSource
from adwords.adapters import PlacementPerformanceReportAdapter


class PlacementPerformanceReportDataSource(PerformanceReportDataSource):
    def __init__(self, storage, path):
        super(PlacementPerformanceReportDataSource, self).__init__(
            storage=storage,
            path=path,
            name="PLACEMENT_PERFORMANCE_REPORT",
            adapters=(PlacementPerformanceReportAdapter,)
        )
