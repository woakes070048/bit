# coding=utf-8
from __future__ import absolute_import, unicode_literals
from .performance import PerformanceReportDataSource
from adwords.adapters import GenderPerformanceReportAdapter


class GenderPerformanceReportDataSource(PerformanceReportDataSource):
    def __init__(self, storage, path):
        super(GenderPerformanceReportDataSource, self).__init__(
            storage=storage,
            path=path,
            name="GENDER_PERFORMANCE_REPORT",
            adapters=(GenderPerformanceReportAdapter,)
        )

