# system
import os
from io import BytesIO

import petl
import zlib
import logging
from datetime import datetime, timedelta
import zipfile

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# superset
from superset import app
from superset import cache

# local
from bit.utils.conversions import sqla_python_types
from bit.models import Connector

# from . import  GoogleDriveStorage

from .. datasources.campaign import CampaignPerformanceReportDataSource

from .. settings import CONNECTOR_INFO

DB_PREFIX = '{}'.format(
    app.config.get('APP_DB_PREFIX', 'bit'),
)

class AdWordsConnector(Connector):
    """AdWords: Model Auth connector"""

    __tablename__ = '{}_adwords_connector'.format(DB_PREFIX)

    __mapper_args__ = {
        'polymorphic_identity': 'adwords'
    }

    # ForeignKey to Connector (Parent)
    id = Column(Integer, ForeignKey('bit_connectors.id'), primary_key=True)


    # change to text field and use storage as package
    storage = relationship(
        'GoogleDriveStorage',
        # uselist=False,
        cascade='all,delete',
        back_populates='connector'
    )

    storage_path = Column(String(255), default='bit')

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
        """ String: connector info. """
        # change url
        html = '<h4><a href="/adwordsconnectorview/list/">{name}</a></h4>' \
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
    report_filename_pat = report_folder + '/{report}_{from_date}_{to_date}.csv'
    data = {}
    report = ''
    from_date = ''
    to_date = ''


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


    def get_report_filename(self, report='', from_date='', to_date=''):
        # String: get_report_filename by report name and dates

        if not (report or from_date or to_date):
            return False

        return self.report_filename_pat.format(
            report=report,
            from_date=from_date,
            to_date=to_date
        )

    def download(self, path=''):

        logging.info('Start download from google drive')
        logging.info(path)

        report_filename = self.get_report_filename(
            self.report, self.from_date, self.to_date
        )
        if cache:
            cache_key = path
            cache_timeout = CONNECTOR_INFO.get('report_cache_timeout', 60 * 60)

            z_report = cache.get(cache_key)
            if z_report is not None:
                return petl.io.fromjson(petl.MemorySource(
                    zlib.decompress(z_report)
                ))


            logging.info('Download Report from {}'.format(path))

            storage = self.storage[0]
            storage.init()

            fname = '{}.json'.format(self.report)

            with storage.open(path) as archive_file:
                with zipfile.ZipFile(archive_file) as zip_file:
                    # logging.info(fname)
                    report = zip_file.read(fname)
                    z_report = zlib.compress(report)
                    cache.set(cache_key, z_report, timeout=cache_timeout)
                    return petl.io.fromjson(petl.MemorySource(report))
        else:
            # move to init
            if not os.path.exists(self.report_folder):
                os.makedirs(self.report_folder)

            if not os.path.exists(report_filename):
                logging.info('Download Report from {}'.format(path))
                storage = self.storage[0]
                storage.init()

                fname = '{}.json'.format(self.report)

                with storage.open(path) as archive_file:
                    with zipfile.ZipFile(archive_file) as zip_file:
                        # logging.info(fname)
                        report = zip_file.read(fname)

                        with open(report_filename, 'wb') as f:
                            f.write(report)

                        logging.info('Read from {}'.format(report_filename))
                        report = petl.io.fromjson(report_filename)
                        return report
        return []

    def get_data(self, report='', from_date='', to_date=''):

        if not (report or from_date or to_date):
            return False
        # report_url = self.get_report_url(report, from_date, to_date)

        self.report = report
        self.from_date = from_date
        self.to_date = to_date

        # self.from_date = '2017-09-16'

        folder = '{}/{}'.format(
            self.storage_path,
            self.from_date
        )
        archive_path = '{}/{}.zip'.format(folder, self.report)

        if not archive_path:
            return False

        raw_data = self.download(archive_path)

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

    # TODO DELETE THIS
    def get_data_sources(self):
        storage = self.storage[0]
        storage.init()

        dss = (
            CampaignPerformanceReportDataSource,
        )

        for klass in dss:
            # change to get first storage
            yield klass(storage=storage, path=self.storage_path)

    def sync_adwords_campaign_performance_report(self):

        logging.info('Start sync adwords')

        for ds in self.get_data_sources():
            logging.info("Processing data source: {0}".format(ds.name))
            ds.sync()
        return {}
