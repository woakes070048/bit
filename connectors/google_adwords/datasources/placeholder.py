# coding=utf-8
from __future__ import absolute_import, unicode_literals
from .performance import PerformanceReportDataSource
from adwords.adapters import PlaceHolderPerformanceReportAdapter


class PlaceHolderPerformanceReportDataSource(PerformanceReportDataSource):
    def __init__(self, storage, path):
        super(PlaceHolderPerformanceReportDataSource, self).__init__(
            storage=storage,
            path=path,
            name="PLACEHOLDER_FEED_ITEM_REPORT",
            adapters=(PlaceHolderPerformanceReportAdapter,)
        )
