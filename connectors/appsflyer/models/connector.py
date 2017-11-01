# python 2to3
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

# system
import zlib
import hashlib
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

    data_sources = CONNECTOR_INFO.get('reports', {})
    fields_types = CONNECTOR_INFO.get('fields_types', {})
    replace_values = CONNECTOR_INFO.get('replace_values', {})
    replace_in_values = CONNECTOR_INFO.get('replace_in_values', {})

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

        # logging.info('{} info'.format(self.connector_name))

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
    report_filename_pat = report_folder + '/{hash}.csv'
    data = {}
    report = ''
    from_date = ''
    to_date = ''

    def web_test(self):

        logging.info('web_test[{}]'.format(CONNECTOR_INFO.get('key')))
        return True

    def get_report_urls(self, report='', from_date='', to_date=''):
        # String: url by report name and dates

        if not (report or from_date or to_date):
            return False

        urls = []

        if self.app_id:
            app_ids = self.app_id.split(',')

            for app_id in app_ids:
                if app_id:
                    urls.append(
                        self.url_pat.format(
                            app_id=app_id,
                            api_token=self.api_token,
                            report=report,
                            from_date=from_date,
                            to_date=to_date
                        )
                    )
        return urls

    def get_report_filename(self, hash=''):
        # String: get_report_filename by report name and dates

        if not hash:
            return False

        return self.report_filename_pat.format(hash=hash)

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

        columns = []

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

    def download(self, urls=[]):

        # timeout setting for requests
        # timeout = urllib3.Timeout(connect=2.0, read=7.0)
        # http = urllib3.PoolManager(timeout=timeout)
        http = urllib3.PoolManager()

        report_data = []

        for url in urls:

            report_filename = self.get_report_filename(
                hashlib.md5(url).hexdigest())

            if cache:
                cache_key = url
                cache_timeout = CONNECTOR_INFO.get(
                    'report_cache_timeout', 60 * 60
                )

                z_report = cache.get(cache_key)
                if z_report is not None:

                    if not report_data:
                        report_data = petl.io.fromcsv(petl.MemorySource(
                            zlib.decompress(z_report)
                        ))

                    report_data = petl.stack(
                        report_data,
                        petl.io.fromcsv(petl.MemorySource(
                            zlib.decompress(z_report)
                        ))
                    )

                    continue

                logging.info('Download Report from {}'.format(url))

                r = http.request(
                    'GET',
                    url,
                    retries=urllib3.Retry(
                        redirect=2,
                        backoff_factor=2,
                    )
                )
                if r.status == 200:
                    report = r.data
                    r.release_conn()

                    z_report = zlib.compress(report)
                    cache.set(cache_key, z_report, timeout=cache_timeout)

                    # return petl.io.fromcsv(petl.MemorySource(report))

                    if not report_data:
                        report_data = petl.io.fromcsv(
                            petl.MemorySource(report))

                    report_data = petl.stack(
                        report_data,
                        petl.io.fromcsv(petl.MemorySource(report))
                    )
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
                        if not report_data:
                            report_data = petl.io.fromcsv(report_filename)
                        report_data = petl.stack(
                            report_data,
                            petl.io.fromcsv(report_filename)
                        )
        return report_data

    def get_data(self, report='', from_date='', to_date=''):

        if not (report or from_date or to_date):
            return False

        self.report = report
        self.from_date = from_date
        self.to_date = to_date

        report_urls = self.get_report_urls(report, from_date, to_date)

        if not report_urls:
            return False

        raw_data = self.download(report_urls)

        if not raw_data:
            self.data = []
            return False

        self.data = raw_data

        if len(self.replace_values):
            for field in self.replace_values:
                if len(self.replace_values[field]):
                    try:
                        self.data = petl.convert(
                            self.data, field, self.replace_values[field]
                        )
                    except Exception as e:
                        # no field exist
                        logging.exception('No {} field exist'.format(
                            field
                        ))
                        pass

        if len(self.replace_in_values):
            for field in self.replace_in_values:
                if len(self.replace_in_values[field]):
                    try:
                        self.data = petl.convert(
                            self.data,
                            field,
                            'replace',
                            self.replace_in_values[field][0],
                            self.replace_in_values[field][1]
                        )
                    except Exception as e:
                        # no field exist
                        logging.exception('No {} field exist'.format(
                            field
                        ))
                        pass

        if len(self.fields_types):

            converts = {}

            for col in self.data[0]:
                converts.update({
                    col: sqla_python_types.get(
                        self.fields_types.get(col, 'String'),
                        str
                    ),
                })

            self.data = petl.convert(self.data, converts)
