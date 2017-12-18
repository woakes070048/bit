# system
import petl
import sqlparse
from logging import getLogger
from datetime import datetime, timedelta
from dateutil import parser as dateutil_parser

# sqlalchemy
import sqlalchemy as sa
from sqlalchemy import asc
from sqlalchemy import table
from sqlalchemy import select
from sqlalchemy import column
from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.engine import reflection
from sqlalchemy.schema import CreateSchema
from sqlalchemy.schema import CreateTable
from sqlalchemy.schema import DropTable

# superset
from superset import utils
from superset import app
from superset.jinja_context import get_template_processor

# do not delete. need ot on fly create hstore column
from sqlalchemy.dialects import postgresql

# flask
from flask import flash
from flask_appbuilder import Model
from flask_babel import lazy_gettext as _

# superset
from superset import app
from superset import db
# from superset import create_app
from superset import sm
from superset.connectors.base.models import BaseDatasource
from superset.utils import send_email_smtp
from superset.connectors.sqla.models import SqlaTable

# locale
from bit.utils.etl_status import EtlStatus

# app, db, migrate = create_app()


logger = getLogger(__name__)
stats_logger = app.config.get('STATS_LOGGER')
MODULE_NAME = 'etl'
DB_PREFIX = '{}_{}'.format(
    app.config.get('APP_DB_PREFIX', 'bit'),
    MODULE_NAME
)
# Default schema for etl tables
DB_ETL_SCHEMA = 'bit_etl'
# Default Prefix for etl tables
DB_ETL_PREFIX = '_etl'


class EtlPeriod(object):
    EMPTY = 0
    ONEMONTH = 60 * 60 * 24 * 30
    ONEWEEK = 60 * 60 * 24 * 7
    ONEDAY = 60 * 60 * 24
    ONEHOUR = 60 * 60
    HALFHOUR = 30 * 60
    MINUTE = 1 * 60

    ALL = [EMPTY, ONEMONTH, ONEWEEK, ONEDAY, ONEHOUR, HALFHOUR, MINUTE]

    CHOICES = (
        (EMPTY, 'No schedule'),
        (ONEMONTH, _('Monthly')),
        (ONEWEEK, _('Weekly')),
        (ONEDAY, _('Daily')),
        (ONEHOUR, _('Hourly')),
        (HALFHOUR, _('Half-hourly')),
        (MINUTE, _('Minutely')),
    )

    HOURS = (
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
        (11, '11'),
        (12, '12'),
        (13, '13'),
        (14, '14'),
        (15, '15'),
        (16, '16'),
        (17, '17'),
        (18, '18'),
        (19, '19'),
        (20, '20'),
        (21, '21'),
        (22, '22'),
        (23, '23'),
    )

    @classmethod
    def get_by_seconds(cls, seconds=0):
        r = [period for period in cls.CHOICES if
             seconds in period]
        if r:
            return str(r[0][1])
        return str(cls.CHOICES[cls.EMPTY][1])


# need for Superset metrics permissions
class EtlMetric(Model):
    """Default Metric Class For Superset Init."""

    __tablename__ = '{}_table_metrics'.format(DB_PREFIX)  # sql table name

    id = Column(Integer, primary_key=True)
    type = 'etl'


# class EtlTable(Model, AuditMixinNullable):
class EtlTable(Model, BaseDatasource):
    """
    Play class for integrate ETL
    Use existing functionality superset tables and columns
    """
    type = 'etl'

    __tablename__ = '{}_tables'.format(DB_PREFIX)  # sql table name

    # need for superset metrics permissions
    metric_class = EtlMetric

    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, index=True, nullable=False)

    datasource = Column(String(250))

    # by default we save all new tables in etl schema. on future we can allow
    # to save for any schema user set
    schema = Column(String(255), default=DB_ETL_SCHEMA)
    sync_field = Column(String(250), default='id')
    sync_last = Column(String(250), default='')
    sync_last_time = Column(DateTime, default=datetime.utcnow)
    sync_next_time = Column(DateTime, default=datetime.utcnow)
    sync_periodic = Column(Integer, default=0)
    sync_periodic_hour = Column(Integer, default=0)

    chunk_size = Column(Integer, default=1)
    status = Column(String(16), default=EtlStatus.STOPPED)
    # progress = Column(Integer, default=0)  # 1..100
    progress = Column(Numeric, default=0)  # 1..100
    calculate_progress = Column(Boolean, default=True)
    downloaded_rows = Column(Integer, default=0)
    is_valid = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    is_scheduled = Column(Boolean, default=False)
    save_in_prt = Column(Boolean, default=False)

    # Relation
    # ForeignKey to Connector (Parent)

    connector_id = Column(Integer, ForeignKey('bit_connectors.id'))
    connector = relationship(
        'Connector',
        backref=backref('etl_tables', cascade='all, delete-orphan'),
        foreign_keys=[connector_id])

    # Relation
    table_id = Column(Integer, ForeignKey('tables.id'))
    table = relationship(
        'SqlaTable',
        backref=backref('etl_tables', cascade='all, delete-orphan'),
        foreign_keys=[table_id])

    # Relation
    user_id = Column(Integer, ForeignKey('ab_user.id'))
    owner = relationship(
        sm.user_model,
        backref='etl_tables',
        foreign_keys=[user_id])

    def __repr__(self):
        return self.name

    @property
    def schema_perm(self):
        """Returns schema permission if present, database one otherwise."""
        return 'bit_etl'
        # return utils.get_schema_perm(self.database, self.schema)

    def get_perm(self):
        return (
            '[{obj.sql_table_name}]'
            '(id:{obj.id})').format(obj=self)

    @property
    def repr_sync_periodic(self):
        return EtlPeriod.get_by_seconds(self.sync_periodic)

    @property
    def sql_table_name(self):
        return '{}_{}'.format(DB_ETL_PREFIX, self.name)

    @property
    def inspector(self):
        return reflection.Inspector.from_engine(self.local_engine)

    @property
    def local_engine(self):
        """Local DataBase"""
        return db.engine

    @property
    def remote_engine(self):
        """Remote DataBase"""
        return self.table.database.get_sqla_engine()

    def get_template_processor(self, **kwargs):
        return get_template_processor(
            table=self.table, database=self.table.database, **kwargs)

    def all_schema_names(self):
        """Return all schema names in referred"""

        logger.info('all_schema_names')
        logger.info(self.inspector.get_schema_names())
        return self.inspector.get_schema_names()

    def all_table_names(self):
        """Return all tables names in referred"""

        logger.info('all_table_names')
        logger.info(self.inspector.get_table_names(self.schema))
        return self.inspector.get_table_names(self.schema)

    def get_sqla_table(self):
        tbl = table(self.table.table_name)
        if self.schema:
            tbl.schema = self.schema
        return tbl

    def exist_schema(self):
        return self.schema in self.all_schema_names()

    def create_schema(self):
        logger.info('try to create schema {}'.format(self.schema))
        if self.exist_schema():
            return True
        return self.local_engine.execute(CreateSchema(self.schema))

    def exist_table(self):
        return self.sql_table_name in self.all_table_names()

    def cccc(self):

        sqt = SqlaTable()

        # sqt.database =
        sqt.schema = self.schema
        sqt.table_name = self.sql_table_name
        sqt.database = 'main'
        sqt.schema = 'main'
        sqt.table_name = 'main'

        return False

    def create_table(self):

        if not self.schema:
            self.schema = DB_ETL_SCHEMA

        if not self.create_schema():
            return False

        logger.info('try to create table {} in {}'.format(
            self.sql_table_name,
            self.schema
        ))

        if self.exist_table():
            return True

        table = self.get_sql_table_object(need_columns=True)
        return self.local_engine.execute(CreateTable(table))

    def delete_table(self):
        logger.info('try to delete table {} in {}'.format(
            self.sql_table_name,
            self.schema
        ))

        table = self.get_sql_table_object(need_columns=False)
        return self.local_engine.execute(DropTable(table))

    def tmp_table(self):
        extra = {}
        meta = MetaData(**extra.get('metadata_params', {}))
        return Table(
            self.sql_table_name, meta,
            schema=self.schema or None,
            autoload=True,
            autoload_with=self.local_engine)

    def get_columns_from_etl_table(self):
        try:
            extra = {}
            meta = MetaData(**extra.get('metadata_params', {}))
            table = Table(
                self.sql_table_name, meta,
                schema=self.schema or None,
                autoload=True,
                autoload_with=self.local_engine)

        except Exception:

            raise Exception(
                "Table doesn't seem to exist in the specified database, "
                "couldn't fetch column information")

        return len(table.columns)

    def etl_not_valid(self, err=''):

        self.is_valid = False
        self.is_scheduled = False
        db.session.merge(self)
        db.session.commit()

        msq = '[etl_not_valid] {}'.format(
            err[:1000]
        )
        logger.exception(msq)

        # TODO SET USER OBJECT

        # send user email
        email = 'chiter2008@gmail.com'
        subject = 'Etl table ({}) not valid'.format(self.sql_table_name)

        # move to template emails
        message = 'Etl table <b>({table_name})</b>, ' \
                  'has changed.<br/>Please login ' \
                  'and repair or create new table.'.format(
                        table_name=self.sql_table_name
                  )
        send_email_smtp(email, subject, message, app.config,
                        dryrun=not app.config.get('EMAIL_NOTIFICATIONS'))
        raise Exception('[etl_not_valid] {}'.format(
            err[:1000]
        ))

    def clear_sql(self):
        """"Remove orders and limits from query"""

        if not self.table.sql:
            return ''

        # logging.info('Original sql query')
        sql = sqlparse.format(
            self.table.sql,
            reindent=True,
            keyword_case='upper'
        ).strip()

        # logging.info(sql)
        sql_statement = sqlparse.parse(sql)[0]

        if sql_statement.get_type() != 'SELECT':
            raise Exception('Allow only SELECT statement')

        # logging.info("statement_sql is SELECT")
        sql_new_statement = []

        for sql_token in sql_statement.tokens:
            # if sql_token.value in ['ORDER', 'LIMIT']:
            if sql_token.value in ['LIMIT']:
                break
            sql_new_statement.append(str(sql_token))

        # logging.info("Parsed sql query")
        sql_new_statement = u''.join(sql_new_statement)

        # logging.info(sql_new_statement)

        if self.sync_last != '':
            print(self.sync_last)
            tp = self.get_template_processor(sync_last=self.sync_last)
        else:
            tp = self.get_template_processor()

        sql_new_statement = tp.process_template(sql_new_statement)

        return sql_new_statement

    def remote_etl_sql(self):
        """SQL QUERY FOR RESULTS FROM REMOTE SOURCE"""
        if not self.table.sql:
            """Use table name."""
            try:
                columns = {col.column_name: col for col in self.table.columns}

                sql = select([]).select_from(self.get_sqla_table())

                if self.sync_field and self.sync_field in columns:
                    sql = sql.where(column(self.sync_field) > self.sync_last)
                    sql = sql.order_by(asc(self.sync_field))

                return sql
            except Exception as e:
                logger.exception(str(e))
                raise
        else:
            """Use custom sql query."""
            try:

                return self.clear_sql()

            except Exception as e:
                logger.exception(str(e))
                raise

    def remote_sql_count(self):
        """SQL QUERY FOR COUNT ROW IN REMOTE SOURCE"""
        try:
            return 'SELECT COUNT(*) AS rows_count FROM ({sql}) AS CHITER;'. \
                format(
                    sql=self.remote_etl_sql().compile(
                        compile_kwargs={"literal_binds": True})
                )
        except AttributeError:
            return 'SELECT COUNT(*) AS rows_count FROM ({sql}) AS CHITER;'. \
                format(
                    sql=self.remote_etl_sql()
                )

    def locale_sql_count(self):
        sql = ''
        if self.schema and self.sql_table_name:
            """Use schema and table name"""
            try:
                sql = 'SELECT COUNT(*) AS rows_count FROM {schema}.{table};'.\
                    format(
                        schema=self.schema,
                        table=self.sql_table_name
                    )
            except Exception as e:
                logger.exception(str(e))
        elif self.sql_table_name:
            """Use table name"""
            try:
                sql = 'SELECT COUNT(*) AS rows_count FROM {table};'.format(
                    table=self.sql_table_name
                )
            except Exception as e:
                logger.exception(str(e))

        return sql

    def sync(self):

        msq = 'Run Sync EtlId ({})'.format(self.id)
        print(msq)
        logger.info(msq)

        if self.status == EtlStatus.RUNNING:
            msq = 'Task Already running'
            print(msq)
            logger.exception(msq)
            raise Exception(msq)

        self.status = EtlStatus.PENDING
        self.downloaded_rows = 0
        self.progress = 0

        db.session.merge(self)
        db.session.commit()

        # count columns in local table
        etl_table_columns_count = self.get_columns_from_etl_table()
        print('etl_table_columns_count {}'.format(etl_table_columns_count))

        # connect to remote database
        with self.remote_engine.connect() as remote_connection:
            # connect to locale database
            with self.local_engine.connect() as local_connection:

                if self.calculate_progress:
                    locale_table_rows_count = local_connection.execute(
                        self.locale_sql_count()).fetchone()['rows_count']

                    print('locale_table_rows_count {}'.format(
                        locale_table_rows_count))

                    remote_table_rows_count = remote_connection.execute(
                        self.remote_sql_count()).fetchone()['rows_count']

                    print('remote_table_rows_count {}'.format(
                        remote_table_rows_count))

                # ----------------------------

                remote_sql = self.remote_etl_sql()

                print(remote_sql)

                rc_result = remote_connection.execution_options(
                    stream_results=True
                ).execute(remote_sql)

                rc_cursor = rc_result.cursor

                rt_columns_names = [col[0] for col in rc_cursor.description]

                # count remote cols
                remote_table_columns_count = len(rt_columns_names)

                print('remote_table_columns_count {}'.format(
                    remote_table_columns_count))

                # compare local and remote columns count
                if remote_table_columns_count != etl_table_columns_count:
                    # print('etl_not_valid 1')
                    self.etl_not_valid('remote_cols != locale_cols')

                while True:

                    if self.status == EtlStatus.STOPPED:
                        break

                    chunks = rc_cursor.fetchmany(self.chunk_size)

                    result_count = len(chunks)

                    print('next {} rows'.format(result_count))

                    # print('Row count from db {}'.format(result_count))

                    add_rows = []

                    if chunks:
                        for chunk in chunks:
                            add_rows.append(
                                dict(zip((c for c in rt_columns_names), chunk))
                            )

                    # complete
                    if not add_rows:
                        self.status = EtlStatus.SUCCESS
                        self.progress = 100
                        self.sync_last_time = datetime.utcnow().replace(
                            microsecond=0
                        )
                        self.sync_next_time = self.get_next_sync()
                        self.is_scheduled = False
                        db.session.merge(self)
                        db.session.commit()
                        break

                    # print(add_rows)

                    try:
                        # add new rows to local table
                        local_connection.execute(
                            self.get_sql_table_object(
                                need_columns=False
                            ).insert(),
                            add_rows
                        )

                        try:
                            last = add_rows[-1]

                            self.sync_last = last[self.sync_field]
                            self.status = EtlStatus.RUNNING
                            self.downloaded_rows = self.downloaded_rows + result_count

                            if self.calculate_progress:
                                locale_table_rows_count = locale_table_rows_count + result_count
                                progress = float(
                                    100 * (float(
                                        locale_table_rows_count
                                    ) / float(
                                        remote_table_rows_count
                                    ))
                                )
                                self.progress = round(progress, 4)

                            db.session.merge(self)
                            db.session.commit()
                        except Exception as e:
                            self.etl_not_valid(e)

                    except Exception as e:
                        self.etl_not_valid(e)
        # db.engine.dispose()
        return True

    def sync_delay(self):

        if self.status == EtlStatus.RUNNING:
            msq = 'Task Already running'
            print(msq)
            logger.exception(msq)
            raise Exception(msq)

        from bit.tasks import async_etl
        async_etl.delay(etl_id=self.id)

    def stop(self):
        """ Stop ETL TASK. """

        if self.status != EtlStatus.STOPPED:
            self.status = EtlStatus.STOPPED
            self.is_scheduled = False
            self.sync_last_time = datetime.utcnow().replace(
                microsecond=0
            )
            self.sync_next_time = self.get_next_sync()

            db.session.merge(self)
            db.session.commit()

    def clear(self):
        """ Stop ETL TASK and Clear ETL local table """

        dt = datetime.utcnow().replace(
            microsecond=0
        )

        self.status = EtlStatus.STOPPED
        self.sync_last = ''
        self.sync_last_time = dt
        self.sync_periodic = 0
        self.is_scheduled = False
        # self.chunk_size = 0
        self.progress = 0
        self.sync_next_time = self.get_next_sync()

        db.session.merge(self)
        db.session.commit()

        table_name = self.sql_table_name

        if self.schema and self.sql_table_name:
            table_name = '{schema}.{table}'.format(
                schema=self.schema,
                table=self.sql_table_name
            )
        sql_truncate = 'TRUNCATE TABLE {} CONTINUE IDENTITY RESTRICT;'.format(
            table_name
        )

        with self.local_engine.connect() as local_conection:
            local_conection.execution_options(
                autocommit=True
            ).execute(sql_truncate)

    def sync_once(self):
        """ For test. """

        # logging.info('Try Run Test Sync {}'.format(self.sql_table_name))

        if self.status == EtlStatus.RUNNING:
            raise Exception('Task Already running')

        connector_type = self.get_connector_type()

        if connector_type == 'SQL':

            logger.info('SQL')

            sql = self.remote_etl_sql()

            locale_cols_count = self.get_columns_from_etl_table()

            # add rows
            add_rows = []
            with self.remote_engine.connect() as remote_con:
                rs = remote_con.execute(self.remote_sql_count()).fetchone()
                logger.info(self.remote_sql_count())
                r_rows_count = rs['rows_count']

                rs = remote_con.execute(sql)
                logger.info(sql)
                cursor_description = rs.cursor.description
                remote_cols_count = len(cursor_description)

                if remote_cols_count != locale_cols_count:
                    self.etl_not_valid()

                for row in rs:
                    add_row = {}
                    for row_column, row_value in row.items():
                        add_row.update({str(row_column): row_value})
                    add_rows.append(add_row)

            if not add_rows:
                self.status = EtlStatus.SUCCESS
                self.progress = 100
                db.session.merge(self)
                db.session.commit()
                return False

            # insert to local db
            with self.local_engine.connect() as local_con:
                rs = local_con.execute(self.locale_sql_count()).fetchone()
                l_rows_count = rs['rows_count']
                try:
                    local_con.execute(
                        self.get_sql_table_object(need_columns=False).insert(),
                        add_rows
                    )
                except Exception as e:
                    self.etl_not_valid(str(e))

            try:
                last = add_rows[-1]
                progress = float(
                    100 * (float(l_rows_count) / float(r_rows_count))
                )
                progress = round(progress, 4)
                logger.info(progress)

                self.sync_last = last[self.sync_field]
                self.status = EtlStatus.STOPPED
                self.sync_last_time = datetime.utcnow()
                self.progress = progress

                # save to db
                db.session.merge(self)
                db.session.commit()
            except Exception as e:
                self.etl_not_valid(str(e))

        elif connector_type == 'CONNECTOR':

            logger.info('Connector :)')

            if self.sync_field == 'date':

                from_date = dateutil_parser.parse(self.sync_last)

                if self.connector.type == 'appsflyer':
                    from_date = (
                        dateutil_parser.parse(
                            self.sync_last
                        ) + timedelta(
                             days=1
                        )
                    )

                if from_date.date() >= datetime.utcnow().date():
                    flash(_('Day not started'), 'danger')
                    raise Exception('Day not started')

                to_date = from_date + timedelta(days=self.chunk_size)
                if to_date.date() >= datetime.utcnow().date():
                    to_date = datetime.utcnow() - timedelta(days=1)

                # lmsg = '{} save_in_prt() -> {} -> {}'.format(
                #     self.datasource,
                #     self.save_in_prt,
                #     from_date.date().isoformat(),
                #     to_date.date().isoformat()
                # )
                #
                # logging.info(lmsg)

                last_sync = self.connector.get_data(
                    self.datasource,
                    from_date.date().isoformat(),
                    to_date.date().isoformat(),
                )

                rows = self.connector.data

                # logging.info(rows)

                # add rows
                add_rows = []

                for row in petl.dicts(rows).list():
                    add_row = {}
                    for column, value in row.items():
                        add_row.update(
                            {self.clear_column_name(str(column)): value}
                        )
                    add_rows.append(add_row)

                if not add_rows:
                    self.status = EtlStatus.SUCCESS
                    self.progress = 100
                    db.session.merge(self)
                    db.session.commit()
                    return False

                # print(len(add_rows))

                # insert to local db
                with self.local_engine.connect() as local_con:
                    rs = local_con.execute(self.locale_sql_count()).fetchone()
                    l_rows_count = rs['rows_count']
                    try:
                        local_con.execute(
                            self.get_sql_table_object(
                                need_columns=False).insert(),
                            add_rows
                        )
                    except Exception as e:
                        self.etl_not_valid(str(e))

                # insert to ptr
                # TODO REWRIE
                if self.save_in_prt:
                    # logging.info(self.save_in_prt)
                    # logging.info(self.connector.type)
                    if self.connector.type == 'adwords':
                        # from data_adapter import AdwordsPerformanceReportAdapter
                        from connectors.google_adwords.adapters import CampaignPerformanceReportAdapter
                        CampaignPerformanceReportAdapter.bulk_adapt(add_rows)

                try:
                    # last = from_date
                    # progress = float(
                    #     100 * (float(l_rows_count) / float(r_rows_count))
                    # )
                    # progress = round(progress, 4)
                    # logging.info(progress)

                    self.sync_last = to_date.date().isoformat()

                    # get last sync information from connector and save it
                    # self.sync_last = self.connector.sync_last.isoformat()
                    self.status = EtlStatus.STOPPED
                    self.sync_last_time = datetime.utcnow()
                    self.progress = 100
                    # self.progress = progress

                    # save to db
                    db.session.merge(self)
                    db.session.commit()
                except Exception as e:
                    self.etl_not_valid(str(e))


        return True

    def get_next_sync(self):

        if self.sync_periodic:
            logger.info(self.sync_periodic)

            utc_time_clear = datetime.utcnow().replace(
                # minute=0,
                second=0,
                microsecond=0
            )

            if self.sync_periodic > EtlPeriod.ONEHOUR:
                utc_time_clear = utc_time_clear.replace(
                    hour=self.sync_periodic_hour,
                    minute=0,
                )

            logger.info(utc_time_clear)

            if self.sync_periodic == EtlPeriod.ONEDAY:
                sync_next_time = utc_time_clear
                if utc_time_clear < datetime.utcnow():
                    sync_next_time = utc_time_clear + timedelta(
                        seconds=self.sync_periodic
                    )
            else:
                sync_next_time = utc_time_clear + timedelta(
                    seconds=self.sync_periodic
                )
            logger.info(sync_next_time)

            return sync_next_time

        return None

    def get_sql_table_object(self, need_columns=True):
        if need_columns:
            return Table(
                self.sql_table_name,
                db.metadata,
                schema=self.schema,
                *self.get_columns()
            )
        else:
            return self.tmp_table()

    @classmethod
    def clear_column_name(cls, column_name=''):
        if column_name:
            column_name = column_name.strip().lower().replace(
                ' ', '_'
            ).replace('(', '').replace(')', '').replace('/', '')
        return column_name

    @classmethod
    def clear_column_type(cls, column_type=''):
        if column_type:
            column_type = column_type.split(') ')
            l = len(column_type)
            column_type = column_type[0]
            if l:
                if l > 1:
                    column_type = '{})'.format(column_type)

            column_type = 'sa.{}'.format(column_type)

            if 'INTEGER' in column_type or 'TINYINT' in column_type\
                    or 'BIGINT' in column_type:
                column_type = 'sa.Integer()'

            if 'string' in column_type:
                column_type = 'sa.Text()'

            if 'OBJECT' in column_type:
                column_type = 'sa.Text()'

            if 'DATETIME' in column_type or 'TIMESTAMP WITHOUT TIME ZONE' \
                    in column_type or 'TIMESTAMP WITH TIME ZONE'\
                    in column_type:
                column_type = 'sa.DateTime()'

            if 'HSTORE' in column_type:
                # column_type = 'postgresql.HSTORE(text_type=sa.Text())'
                column_type = 'postgresql.HSTORE'
        else:
            column_type = 'sa.Text()'

        return column_type

    def get_connector_type(self):

        if self.table:
            return 'SQL'
        elif self.connector and self.datasource and (
                    self.datasource in self.connector.get_list_data_sources()):
            return 'CONNECTOR'
        return False

    def get_columns(self):

        columns = []

        connector_type = self.get_connector_type()

        logger.info(connector_type)

        if connector_type == 'SQL':
            for column in self.table.columns:
                column_type = self.clear_column_type(column.type)
                try:
                    columns.append(
                        Column(
                            column.column_name,
                            eval(column_type)
                        )
                    )
                except Exception:
                    logger.info('errr {} -> {}'.format(
                        column.column_name,
                        column_type
                    ))
                    columns.append(
                        Column(
                            column.column_name,
                            eval('sa.Text()')
                        )
                    )
            return columns
        elif connector_type == 'CONNECTOR':
            # get columns from api

            logger.info(
                'get columns from connection {} / {}'.format(
                    self.connector,
                    self.datasource,
                )
            )

            tcolumns = self.connector.get_columns(self.datasource)

            logger.info(tcolumns)

            for column in tcolumns:

                column_name = self.clear_column_name(column['name'])
                column_type = self.clear_column_type(column['type'])

                logger.info(column_type)
                logger.info(column_name)

                try:
                    columns.append(
                        Column(
                            column_name,
                            eval(column_type)
                        )
                    )
                except Exception as e:
                    logger.info('errr {} -> {}'.format(
                        column_name,
                        column_type
                    ))
                    columns.append(
                        Column(
                            column_name,
                            eval('sa.Text()')
                        )
                    )
            logger.info(columns)
            return columns

        raise Exception('Cols not found')
