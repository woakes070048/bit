# system
import json
import logging
import zipfile
from io import BytesIO
from datetime import timedelta
from dateutil import parser

# superset
from superset import app

# BIT
from bit.models.datasource import DataSource

config = app.config


class GoogleDriveDataSource(DataSource):
    def __init__(self, storage, path, source, name, primary_key_column, adapters, models):
        super(GoogleDriveDataSource, self).__init__(
            source=source, name=name, primary_key_column=primary_key_column, adapters=adapters, models=models)
        self._storage = storage
        self._path = path
        self._dates = []
        self._config_file_path = self._path + "/config.json"
        self._config_last_date = None

    def open(self, *args, **kwargs):
        assert self._storage.exists(self._path)

        with self._storage.open(self._config_file_path) as config_file:
            config = json.load(config_file)

        self._config_last_date = parser.parse(config['lastDate']).date()

        prefix_len = len(self._path) + 1

        dirs, files = self._storage.listdir(path=self._path)
        dates = sorted([
           parser.parse(d[prefix_len:]).date()
           for d in dirs
        ])

        # info = self._get_sync_info()

        # if info:
        #    last_date = parser.parse(info.last_id).date()
        #    self._dates = [date for date in dates if last_date < date < self._config_last_date]
        # elif config.get('DATA_SOURCE_START_DATE', None):
            # last_date = parser.parse(config.get('DATA_SOURCE_START_DATE', None)).date() - timedelta(days=1)
            # self._dates = [date for date in dates if last_date < date < self._config_last_date]
        # else:
        #    self._dates = [date for date in dates if date < self._config_last_date]


        last_date = parser.parse('2017-08-18').date() - timedelta(days=1)
        self._dates = [date for date in dates if
                       last_date < date < self._config_last_date]

    def close(self):
        pass

    def fetchmany(self):
        if not len(self._dates):
            return None

        date = self._dates.pop(0)

        logging.info("Fetch data for {0} report {1}".format(date.isoformat(), self.name))

        _dir = "{0}/{1}".format(self._path, date.isoformat())
        archive_path = "{0}/{1}".format(_dir, self.name + ".zip")
        file_name = self.name + ".json"
        with self._storage.open(archive_path) as archive_file:
            with zipfile.ZipFile(archive_file) as zf:
                content = BytesIO(zf.read(file_name))
                content.seek(0)
                rows = json.load(content)

        if not len(rows):
            self._set_last_sync(last={self.primary_key_column: date})
            rows = self.fetchmany()

        return rows
