# python 2to3
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

# system
import zlib

import logging
import os
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
from bit.utils.conversions import sqla_python_types
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

    # no db fields/methods

    data_sources = CONNECTOR_INFO.get('reports')
    fields_types = CONNECTOR_INFO.get('fields_types')

    def connector_name(self):
        """ String: connector name. """
        return CONNECTOR_INFO.get('name', '')

    def connector_description(self):
        """ String: connector description. """
        return CONNECTOR_INFO.get('description', '')

    def connector_logo(self):
        """ String: connector name. """
        logo = '{}/{}/logo.png'.format(
            CONNECTOR_INFO.get('static_folder', ''),
            CONNECTOR_INFO.get('key', '')
        )
        return CONNECTOR_INFO.get('logo_pat', '').format(logo)

    def connector_info(self):

        logging.info('{} info'.format(self.connector_name))

        """ String: connector info. """
        # change url
        html = '<h4><a href="/appsflyerconnectorview/list/">{name}</a></h4>' \
               '{logo}' \
               '<p>{description}</p>'.format(
            name=self.connector_name(),
            logo=self.connector_logo(),
            description=self.connector_description(),
        )
        return html

    def get_list_data_sources(self):
        return self.data_sources

    def admin_data_sources(self):
        """ List: data_sources(Reports) """

        reports = self.data_sources
        ds = [reports.get(report).get('name') for report in reports]

        html = '<p style="width:250px;">{}</p>'.format(
            '<br/>'.join(sorted(ds))
        )

        return html

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

        if self.data:
            columns = []
            for col in self.data[0]:
                columns.append(
                    {
                        'name': col,
                        'type': self.fields_types.get(col, 'String'),
                    }
                )

        return columns

    def download(self, url=''):

        report_filename = self.get_report_filename(
            self.report, self.from_date, self.to_date
        )

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

        rdata = self.download(report_url)

        if rdata:

            converts = {}

            for col in rdata[0]:
                converts.update({
                    col: sqla_python_types.get(
                        self.fields_types.get(col, 'String'), str
                    ),
                })

            # logging.info(converts)


            # logging.info(rdata[1])


            self.data = petl.convert(rdata, converts)
            # logging.info(self.data[1])
