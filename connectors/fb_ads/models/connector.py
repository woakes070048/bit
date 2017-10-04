# system
import logging
import petl
import zlib
from datetime import datetime, timedelta

# facebookads
from facebookads.api import FacebookAdsApi
from facebookads.adobjects.adsinsights import AdsInsights as fbAdsInsights

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


from facebookads.adobjects.adaccount import AdAccount as fbAdAccount

# superset
from superset import cache

# local
from bit.models import Connector
from bit.utils.conversions import sqla_python_types

from fb import AdAccount
from .. sync_fields import fb_ads_insight_fields
from .. settings import CONNECTOR_INFO as CONNECTOR_INFO


class FacebookConnector(Connector):
    """Facebook: Model Auth connector"""

    __tablename__ = '{}_{}'.format(
        CONNECTOR_INFO.get('table_prefix', ''), 'connector'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'facebook_ads'
    }

    # ForeignKey to Connector (Parent)
    id = Column(Integer, ForeignKey('bit_connectors.id'), primary_key=True)

    # Back relation from Connector To FacebookConnector (Children)
    ad_accounts = relationship(
        'AdAccount',
        cascade='all,delete',
        back_populates='connector'
    )

    # data fields
    uid = Column(String(255), unique=True)
    access_token = Column(String(255))

    # no db fields/methods

    _api_ = None

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
        """ String: connector info. """
        # change url
        html = '<h4><a href="/facebookconnectorview/list/">{name}</a></h4>' \
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

    @property
    def api(self):
        """Singleton Api init."""

        if self._api_ is None:

            log_msg = '[{}] INIT API {}'.format(
                'Facebook',
                self.name
            )
            logging.info(log_msg)

            self._api_ = FacebookAdsApi.init(
                app_id=CONNECTOR_INFO.get('app_id'),
                app_secret=CONNECTOR_INFO.get('app_secret'),
                access_token=self.access_token
            )
        return self._api_


    def sync_ad_accounts(self):
        """Synchronization Facebook AdAccount."""

        self.api  # move to init
        AdAccount.sync(connector=self)

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

        time_range = {
            'since': self.from_date,
            'until': self.to_date
        }

        if cache:
            cache_key = path
            cache_timeout = CONNECTOR_INFO.get('report_cache_timeout',
                                               60 * 60)

            z_report = cache.get(cache_key)
            if z_report is not None:
                return petl.io.fromjson(petl.MemorySource(
                    zlib.decompress(z_report)
                ))

            ###############################

            logging.info('Download Report from {}'.format(path))

            request = fbAdAccount.get_insights(
                # pending=True,
                async=True,
                fields=fb_ads_insight_fields,
                params={
                    'time_increment': 1,
                    # 'limit': 1,
                    'level': fbAdsInsights.Level.ad,
                    # 'breakdowns': report.,
                    'time_range': time_range
                }
            )


            # storage = self.storage[0]
            # storage.init()
            #
            # fname = '{}.json'.format(self.report)
            #
            # with storage.open(path) as archive_file:
            #     with zipfile.ZipFile(archive_file) as zip_file:
            #         # logging.info(fname)
            #         report = zip_file.read(fname)
            #         z_report = zlib.compress(report)
            #         cache.set(cache_key, z_report, timeout=cache_timeout)
            #
            #         return petl.io.fromjson(petl.MemorySource(report))
        # else:
        #     # move to init
        #     if not os.path.exists(self.report_folder):
        #         os.makedirs(self.report_folder)
        #
        #     if not os.path.exists(report_filename):
        #         logging.info('Download Report from {}'.format(path))
        #         storage = self.storage[0]
        #         storage.init()
        #
        #         fname = '{}.json'.format(self.report)
        #
        #         with storage.open(path) as archive_file:
        #             with zipfile.ZipFile(archive_file) as zip_file:
        #                 # logging.info(fname)
        #                 report = zip_file.read(fname)
        #
        #                 with open(report_filename, 'wb') as f:
        #                     f.write(report)
        #
        #                 logging.info(
        #                     'Read from {}'.format(report_filename))
        #                 report = petl.io.fromjson(report_filename)
        #                 return report
        return []

    def get_data(self, report='', from_date='', to_date=''):

        if not (report or from_date or to_date):
            return False
        # report_url = self.get_report_url(report, from_date, to_date)


        self.report = report
        self.from_date = from_date
        self.to_date = to_date

        logging.info(self.report)


        # self.from_date = '2017-08-01'
        #
        # dir = '{}/{}'.format(
        #     self.storage_path,
        #     self.from_date
        # )
        # archive_path = '{}/{}.zip'.format(dir, self.report)
        #
        # if not archive_path:
        #     return False
        #
        # rdata = self.download(archive_path)
        #
        # if rdata:
        #
        #     converts = {}
        #
        #     for col in rdata[0]:
        #         converts.update({
        #             col: sqla_python_types.get(
        #                 self.fields_types.get(col, 'String'), str
        #             ),
        #         })
        #
        #     # logging.info(converts)
        #     # logging.info(rdata[1])
        #
        #     self.data = petl.convert(rdata, converts)
        #
        #     # logging.info(self.data[1])