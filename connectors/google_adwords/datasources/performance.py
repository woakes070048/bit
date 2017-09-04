# coding=utf-8
from __future__ import absolute_import, unicode_literals
from .drive import GoogleDriveDataSource


class PerformanceReportDataSource(GoogleDriveDataSource):
    def __init__(self, storage, path, name, adapters, models):
        super(PerformanceReportDataSource, self).__init__(
            storage=storage,
            path=path,
            source="adwords",
            name=name,
            primary_key_column="Date",
            adapters=adapters,
            models=models,
        )
