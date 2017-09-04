# python 2to3
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

# system

import zlib

import logging
import os
import csv
import urllib3
import petl
from datetime import datetime, timedelta

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

# superset
from superset import cache

# local
from bit.models import Connector
from .. settings import CONNECTOR_INFO


class AppsFlyerConnector(Connector):

    __tablename__ = 'bit_{}_connector'.format(CONNECTOR_INFO.get('key'))

    # ForeignKey to Connector (Parent)
    id = Column(Integer, ForeignKey('bit_connectors.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': CONNECTOR_INFO.get('key')
    }

    app_id = Column(String(255))
    api_token = Column(String(255))
    url_pat = Column(String(255))

    data_sources = CONNECTOR_INFO.get('reports')

    @property
    def get_admin_data_sources(self):
        """ List: data_sources(Reports) """

        return '<br/>'.join(self.data_sources)

    # sync
    report_folder = 'reports/{}'.format(CONNECTOR_INFO.get('key'))
    report_filename_pat = report_folder + '/{app_id}_{report}_{from_date}_{to_date}.csv'
    data = {}
    report = ''
    from_date = ''
    to_date = ''

    def web_test(self):

        logging.info('web_test[{}]'.format(CONNECTOR_INFO.get('key')))

        return True

    def get_report_url(self, report='', from_date='', to_date=''):
        # String: url by report name and dates

        if not (report or from_date or to_date):
            return False

        return self.url_pat.format(
            app_id=self.app_id,
            api_token=self.api_token,
            report=report,
            from_date=from_date,
            to_date=to_date
        )

    def get_report_filename(self, report='', from_date='', to_date=''):
        # String: get_report_filename by report name and dates

        if not (report or from_date or to_date):
            return False

        return self.report_filename_pat.format(
            app_id=self.app_id,
            report=report,
            from_date=from_date,
            to_date=to_date
        )

    def get_columns(self, report='', from_date='', to_date=''):

        self.report = report

        if from_date:
            self.from_date = from_date
        else:
            self.from_date = (datetime.utcnow() - timedelta(
                days=1
            )).date().isoformat()

        if to_date:
            self.to_date = to_date
        else:
            self.to_date = (datetime.utcnow()).date().isoformat()

        # one day
        self.to_date = self.from_date

        if not (report or from_date or to_date):
            return False

        columns = [
            {
                'name': 'name',
                'type': 'string',
            },
            {
                'name': 'date',
                'type': 'date',
            },
            {
                'name': 'cost',
                'type': 'float',
            },
        ]

        self.get_data(self.report, self.from_date, self.to_date)

        # print(petl.columns(table))
        # print(petl.header(table))
        # print(petl.look(petl.typecounts(table, 'Campaign ID')))
        # print(petl.look(petl.parsecounts(table, 'Campaign ID')))
        # look(table)

        # from pprint import pprint

        # if table.len():
        #     # pprint(table[1])
        #
        #     from petl import convert, look
        #
        #     converts = {
        #         'Install Time': '',
        #         'WIFI': bool,
        #         'AppsFlyer ID': int,
        #         'Postal Code': int,
        #     }
        #
        #     table = convert(table, converts)
        #
        #     for x in range(3):
        #
        #         for i, col in enumerate(table[0]):
        #             fs = '{}                            ({}),             {}'.format(
        #                 col, table[x][i], type(table[x][i])
        #             )
        #             print(fs)

        if self.data:
            columns = []
            for col in self.data[0]:
                columns.append(
                    {
                        'name': col,
                        'type': 'string',
                    }
                )

        return columns

    def download(self, url=''):

        report_filename = self.get_report_filename(
            self.report, self.from_date, self.to_date
        )

        logging.info(cache)

        # cache = False

        if cache:
            cache_key = url
            cache_timeout = CONNECTOR_INFO.get('report_cache_timeout', 60 * 60)

            z_report = cache.get(cache_key)
            if z_report is not None:
                return petl.io.fromcsv(petl.MemorySource(
                    zlib.decompress(z_report)
                ))

            logging.info('Download Report from {}'.format(url))

            http = urllib3.PoolManager()
            r = http.request(
                'GET',
                url,
                retries=urllib3.Retry(
                    redirect = 2,
                    backoff_factor=2,
                )
            )
            if r.status == 200:
                report = r.data

                logging.info(report)

                r.release_conn()

                z_report = zlib.compress(report)
                cache.set(cache_key, z_report, timeout=cache_timeout)

                return petl.io.fromcsv(petl.MemorySource(report))
            elif r.status == 403:
                raise Exception(r.data)
            else:
                logging.info(r.data)
                logging.info(r.status)
                logging.info(r.headers)

        else:
            # move to init
            if not os.path.exists(self.report_folder):
                os.makedirs(self.report_folder)

            if not os.path.exists(report_filename):
                logging.info('Download Report from {}'.format(url))
                http = urllib3.PoolManager()
                r = http.request(
                    'GET',
                    url,
                    retries=urllib3.Retry(
                        redirect=2,
                        backoff_factor=2,
                    )
                )
                if r.status == 200:
                    with open(report_filename, 'wb') as f:
                        f.write(r.data)
                    r.release_conn()

                    logging.info('Read from {}'.format(report_filename))
                    report = petl.io.fromcsv(report_filename)
                    return report
        return []

    def get_data(self, report='', from_date='', to_date=''):

        if not (report or from_date or to_date):
            return False

        self.report = report
        self.from_date = from_date
        self.to_date = to_date

        report_url = self.get_report_url(report, from_date, to_date)

        if not report_url:
            return False

        self.data = self.download(report_url)
