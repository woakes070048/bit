from collections import namedtuple
import logging
from dateutil import parser as dateutil_parser
from babel.numbers import parse_decimal
from decimal import Decimal
import datetime

# from django.db import models, transaction
# from django.utils import timezone
from itertools import islice, chain

# superset
from superset import db

# flask_appbuilder
from flask_appbuilder import Model

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# superset
from superset import app

# locale
from bit.utils.db_helper import ModelHelper

DB_PREFIX = '{}'.format(
    app.config.get('APP_DB_PREFIX', 'bit'),
)


class DataSourceInfo(Model, ModelHelper):

    __tablename__ = '{}_data_source_info'.format(DB_PREFIX)  # sql table name

    id = Column(Integer, primary_key=True)

    source = Column(String(255), index=True)
    name = Column(String(255), index=True)
    sync_time = Column(String(255), index=True)
    last_id = Column(String(255), index=True)

    @classmethod
    def get_last_sync(cls, source, name):
        #try:
        data = db.session.query(cls).filter_by(
            source=source,
            name=name,
        ).first()

        logging.info(data)
        #except:
        #    data = None

        # try:
        #     data = cls.objects.get(source=source, name=name)
        # except cls.DoesNotExist:
        #     data = None
        return data

    @classmethod
    def set_last_sync(cls, source, name, sync_time, last_id):
        obj, _ = cls.update_or_create(
            source=source,
            name=name,
            defaults=dict(
                sync_time=sync_time,
                last_id=last_id
            )
        )
        return obj


class DataSource(object):
    def __init__(self, source, name, primary_key_column, adapters, models, chunk_size=1000):
        self.chunk_size = chunk_size
        self.source = source
        self.name = name
        self.primary_key_column = primary_key_column
        self.adapters = adapters
        self.models = models

    def _get_sync_info(self):
        return DataSourceInfo.get_last_sync(source=self.source, name=self.name)

    def _set_last_sync(self, last):

        last_id = last[self.primary_key_column] if isinstance(last, dict) else last.__getattribute__(self.primary_key_column)
        logging.info("Data Source '{0}' update last id {1}".format(self.name, last_id))
        return DataSourceInfo.set_last_sync(
            source=self.source,
            name=self.name,
            sync_time=datetime.datetime.utcnow(),
            last_id=last_id
        )

    @classmethod
    def batch(cls, iterable, size):
        source_iter = iter(iterable)
        while True:
            batch_iter = islice(source_iter, size)
            yield chain([batch_iter.next()], batch_iter)

    def open(self, *args, **kwargs):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def fetchmany(self):
        raise NotImplementedError()

    def sync(self):
        self.open()

        while True:
            chunk = self.fetchmany()
            if not chunk:
                break

                logging.info(
                    "Sync data source {1} rows in {0}".format(
                        len(chunk), self.name
                    )
                )

            # with transaction.atomic():
            # for batch in self.batch(chunk, 1000):
            #     logging.info("Processing batch...")
            for klass in self.adapters:
                logging.info("Processing adapter: {0}".format(klass.__name__))
                klass.bulk_adapt(chunk)

            self._set_last_sync(chunk[-1])

            for klass in self.models:
                for ch in chunk:

                    try:
                        cost = float(ch['Cost'])
                    except:
                        cost = Decimal.from_float(0.0)

                    cost_per_mobile_app_installs = 0
                    if cost:
                        try:
                            cost_per_mobile_app_installs = cost/float(ch['Conversions'])
                        except:
                            pass

                    # single sync in table
                    obj, created = klass.update_or_create(
                        campaign_name=ch['CampaignName'],
                        cost=cost,
                        clicks=int(ch['Clicks']),
                        mobile_app_installs=float(ch['Conversions']),
                        cost_per_mobile_app_installs=cost_per_mobile_app_installs,
                        impression_device=ch['Device'],
                        impressions=float(ch['Impressions']),
                        conversions=float(ch['Conversions']),
                        date=dateutil_parser.parse(ch['Date']).date(),

                        defaults=ch,
                        remove_id=True
                    )

        self.close()

    # def sync(self, engine):
    #     info = self._get_sync_info()
    #     query = self.get_query(last_sync_info=info)
    #     result = engine.execution_options(stream_results=True).execute(query)
    #
    #     row_tuple = namedtuple(self.name, result.keys())
    #
    #     while True:
    #         chunk = result.fetchmany(self.chunk_size)
    #         if not chunk:
    #             break
    #
    #         all_ = [row_tuple(*row) for row in chunk]
    #
    #         logging.info(
    #             "Sync data source {1} rows in  {0} starts from {2}".format(
    #                 len(all_), self.name, info.last_id if info else None
    #             )
    #         )
    #
    #         with transaction.atomic():
    #             for Adapter in self.adapters:
    #                 Adapter.bulk_adapt(all_, engine)
    #             info = self._set_last_sync(all_[-1])


class DbDataSource(DataSource):

    def __init__(self, engine, source, name, primary_key_column, adapters, chunk_size):
        super(DbDataSource, self).__init__(
            source=source,
            name=name,
            primary_key_column=primary_key_column,
            adapters=adapters,
            chunk_size=chunk_size
        )
        self.result = None
        self.row_tuple = None
        self.engine = engine

    def get_query(self, last_sync_info):
        raise NotImplementedError()

    def open(self, *args, **kwargs):
        self.close()
        query = self.get_query(last_sync_info=self._get_sync_info())
        self.result = self.engine.execution_options(stream_results=True).execute(query)
        self.row_tuple = namedtuple("row", self.result.keys())

    def fetchmany(self):
        chunk = self.result.fetchmany(self.chunk_size)
        if chunk:
            chunk = [self.row_tuple(*row) for row in chunk]
        return chunk

    def close(self):
        if self.result:
            self.result.close()
            self.result = None
