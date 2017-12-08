# system
from logging import getLogger
from datetime import datetime, timedelta
from dateutil import parser as dateutil_parser
import sqlparse
import petl

# sqlalchemy
import sqlalchemy as sa
from sqlalchemy import text, table
from sqlalchemy import select
from sqlalchemy import column
from sqlalchemy import bindparam
from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy.orm import backref, relationship
from sqlalchemy.engine import reflection
from sqlalchemy.schema import CreateSchema
from sqlalchemy.schema import CreateTable
from sqlalchemy.schema import DropTable

# superset
from superset import app
from superset.utils import get_celery_app

# do not delete. need ot on fly create hstore column
from sqlalchemy.dialects import postgresql

# flask
from flask import flash
from flask_appbuilder import Model
from flask_babel import lazy_gettext as _

# superset
from superset import app
from superset import db
from superset import sm
from superset.connectors.base.models import BaseDatasource
from superset.utils import send_email_smtp
from superset.connectors.sqla.models import SqlaTable

# locale
from bitstart import app_manager
from bit.utils.etl_status import EtlStatus


logger = getLogger(__name__)

celery_app = get_celery_app(app.config)


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
    sync_last = Column(String(250), default=0)
    sync_last_time = Column(DateTime, default=datetime.utcnow)
    sync_next_time = Column(DateTime, default=datetime.utcnow)
    sync_periodic = Column(Integer, default=0)
    sync_periodic_hour = Column(Integer, default=0)

    chunk_size = Column(Integer, default=1)
    status = Column(String(16), default=EtlStatus.STOPPED)
    # progress = Column(Integer, default=0)  # 1..100
    progress = Column(Numeric, default=0)  # 1..100
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

    @staticmethod
    def etl_not_valid(err=''):
        # logging.exception(err)
        raise Exception('[etl_not_valid] {}'.format(
            err[:1000]
        ))


        # TODO SET USER OBJECT
        # send user email

        email = 'chiter2008@gmail.com'
        subject = 'Etl table ({}) not valid'.format(self.sql_table_name)

        # move to template emails
        message = 'Etl table <b>({table_name})</b>, has changed.<br/>Please login ' \
                  'and repair or create new table.'.format(
                        table_name = self.sql_table_name
                  )
        send_email_smtp(email, subject, message, app.config,
                        dryrun=not app.config.get('EMAIL_NOTIFICATIONS'))

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
            if sql_token.value in ['ORDER', 'LIMIT']:
                break
            sql_new_statement.append(str(sql_token))

        # logging.info("Parsed sql query")
        sql_new_statement = u''.join(sql_new_statement)

        # logging.info(sql_new_statement)
        return sql_new_statement

    def etl_sql(self):
        sql = ''
        if not self.table.sql:
            """Use table name."""
            try:
                # sql = select().where(
                #     column(self.sync_field) > self.sync_last
                # ).order_by(
                #     self.sync_field
                # ).select_from(
                #     table(self.table.table_name)
                # )



                sql = text(
                    'SELECT * FROM :table '
                    'WHERE :pk > :last_pk '
                    'ORDER BY :pk;'
                ).bindparams(
                    bindparam(
                        key='table',
                        value='bit_etl._etl_cities',
                        type_=String
                    ),
                    bindparam(
                        key='pk',
                        value=self.sync_field,
                        type_=String  # TODO Get field from COLUMNS
                    ),
                    bindparam(
                        key='last_pk',
                        value=self.sync_last,
                        type_=String  # TODO Get field from COLUMNS
                    ),
                )

                # sql = text(
                #     'SELECT * FROM :table '
                #     'WHERE :pk > :last_pk '
                #     'ORDER BY :pk;'
                # ).bindparams(
                #     bindparam(
                #         key='pk',
                #         value=self.sync_field,
                #         type_=String  # TODO Get field from COLUMNS
                #     ),
                #     bindparam(
                #         key='last_pk',
                #         value=self.sync_last,
                #         type_=String  # TODO Get field from COLUMNS
                #     ),
                # )
                # sql = 'SELECT * FROM {table} ' \
                #       'WHERE {pk}> \'{pk_last}\' ' \
                #       'ORDER BY {pk} LIMIT {limit};'.\
                #     format(
                #         table=self.table.table_name,
                #         pk=self.sync_field,
                #         pk_last=self.sync_last,
                #         limit=self.chunk_size
                #     )
            except Exception as e:
                logger.exception(str(e))
        else:
            """Use custom sql query."""

            # MACROS
            # try:
            #     template_processor = get_template_processor(
            #         database=database, query=query)
            #     executed_sql = template_processor.process_template(
            #         executed_sql)
            # except Exception as e:
            #     logging.exception(e)
            #     msg = "Template rendering failed: " + utils.error_msg_from_exception(
            #         e)
            #     return handle_error(msg)

            try:
                # sql = select([
                #     text(self.clear_sql().replace('SELECT', ''))
                # ]).where(
                #     column(self.sync_field) > self.sync_last
                # ).order_by(
                #     self.sync_field
                # )

                sql = text(
                    'SELECT * FROM :table '
                    'WHERE :pk > :last_pk '
                    'ORDER BY :pk;'
                ).bindparams(
                    bindparam(
                        key='table',
                        value='_etl_cities',
                        type_=String
                    ),
                    bindparam(
                        key='pk',
                        value=self.sync_field,
                        type_=String  # TODO Get field from COLUMNS
                    ),
                    bindparam(
                        key='last_pk',
                        value=self.sync_last,
                        type_=String  # TODO Get field from COLUMNS
                    ),
                )

                # Query(

                # sql_query = '{query} ' \
                #     'WHERE :pk > :last_pk ' \
                #     'ORDER BY :pk;'.format(
                #         query=self.clear_sql()
                #     )
                # sql = text(sql_query).bindparams(
                #     bindparam(
                #         key='pk',
                #         quote=False,
                #         value=self.sync_field,
                #         type_=Integer  # TODO Get field from COLUMNS
                #     ),
                #     bindparam(
                #         key='last_pk',
                #         value=self.sync_last,
                #         type_=Integer  # TODO Get field from COLUMNS
                #     ),
                # )
                # sql = text(
                #     self.clear_sql()
                # ).where(
                #     user_table.c.name == bindparam('username')
                # )

                # TODO WRITE MACROS SUPPORT

                # sql = 'SELECT * FROM ({sql}) AS CHITER ' \
                #       'WHERE {pk}> \'{pk_last}\' ' \
                #       'ORDER BY {pk} LIMIT {limit};'.\
                #     format(
                #         sql=self.clear_sql(),
                #         pk=self.sync_field,
                #         pk_last=self.sync_last,
                #         limit=self.chunk_size
                #     )
            except Exception as e:
                logger.exception(str(e))

        return sql

    def remote_sql_count(self):
        sql = ''
        if not self.table.sql:
            """Use table name."""
            try:
                sql = 'SELECT COUNT(*) AS rows_count FROM {table};'.format(
                    table=self.table.table_name
                )
            except Exception as e:
                logger.exception(str(e))
        else:
            try:
                sql = 'SELECT COUNT(*) AS rows_count FROM ({sql}) AS CHITER;'.\
                    format(
                        sql=self.clear_sql()
                    )
            except Exception as e:
                logger.exception(str(e))

        return sql

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

    def test_sync_etl(self):

        logger.info('test_sync_etl')

        # tmpsql = """
        #     WITH cities_tracked as  (
        #       select * from cities_city where track=True
        #     )
        #     select * from cities_tracked ORDER BY id;
        #     DELETE cities_tracked;
        #   """
        # print(tmpsql)
        # self.table.sql = tmpsql
        # print(self.clear_sql())


        try:
            sql = self.etl_sql()
            print(sql)
            with self.remote_engine.connect() as remote_con:
                rrs = remote_con.execute(sql)
                # print(rrs.fetchone())

                rrs = remote_con.execute(sql)
                print(rrs.rowcount)
                # print(rrs.fetchone())
                chunks = rrs.fetchmany(self.chunk_size)
                for row in chunks:
                    print(row)
                print('next {} rows'.format(self.chunk_size))
                chunks = rrs.fetchmany(self.chunk_size)
                for row in chunks:
                    print(row)

        except Exception as e:
            logger.exception(e)
            # self.etl_not_valid(str(e))

        # local_db_session = db.session
        #
        # etl_id = 1
        #
        # try:
        #     etl = local_db_session.query(EtlTable).filter_by(id=etl_id).one()
        # except Exception as e:
        #     logger.exception(e)
        #     raise ValueError('Etl not found')



        return True


    # @celery_app.task(ignore_results=True)

    @staticmethod
    def sync(etl_id=0):
        db_session = app_manager.get_db().session()

        try:
            etl = db_session.query(EtlTable).filter_by(id=etl_id).one()
            if etl.status == EtlStatus.RUNNING:
                message = 'Task Already running'
                logger.exception(message)

            # count columns in local table
            locale_cols_count = etl.get_columns_from_etl_table()

            # connect to remote database
            with etl.remote_engine.connect() as remote_con:
                # connect to locale database
                with etl.local_engine.connect() as local_con:

                    # count rows in remote table
                    rrs = remote_con.execute(etl.remote_sql_count()).fetchone()
                    r_rows_count = rrs['rows_count']

                    sql = etl.etl_sql()

                    remote_con.execute(sql)

                    while True:

                        if etl.status == EtlStatus.STOPPED:
                            break

                        add_rows = []

                        # chunk = self.result.fetchmany(self.chunk_size)

                        # rrs = remote_con.execute(sql)
                        cursor_description = rrs.cursor.description

                        # count remote cols
                        remote_cols_count = len(cursor_description)

                        # compare local and remote columns count
                        if remote_cols_count != locale_cols_count:
                            etl.is_valid = False
                            etl.is_scheduled = False
                            db_session.merge(etl)
                            db_session.commit()
                            etl.etl_not_valid(e)

                        for row in rrs:
                            add_row = {}
                            for column, value in row.items():
                                add_row.update({str(column): value})
                            add_rows.append(add_row)

                        # complete
                        if not add_rows:
                            etl.status = EtlStatus.SUCCESS
                            etl.progress = 100
                            etl.sync_last_time = datetime.utcnow().replace(
                                microsecond=0
                            )
                            etl.sync_next_time = etl.get_next_sync()
                            etl.is_scheduled = False
                            db_session.merge(etl)
                            db_session.commit()
                            break

                        try:
                            # add new rows to local table
                            local_con.execute(
                                etl.get_sql_table_object(
                                    need_columns=False
                                ).insert(),
                                add_rows
                            )
                        except Exception as e:
                            etl.is_valid = False
                            etl.is_scheduled = False
                            db_session.merge(etl)
                            db_session.commit()
                            etl.etl_not_valid(e)

                        # count rows in locale table
                        lrs = local_con.execute(etl.locale_sql_count()).fetchone()
                        l_rows_count = lrs['rows_count']

                        try:
                            last = add_rows[-1]

                            progress = float(
                                100 * (float(l_rows_count) / float(r_rows_count))
                            )
                            progress = round(progress, 4)
                            # logging.info(progress)

                            etl.sync_last = last[etl.sync_field]
                            etl.status = EtlStatus.RUNNING
                            etl.progress = progress

                            db_session.merge(etl)
                            db_session.commit()
                        except Exception as e:
                            etl.is_valid = False
                            etl.is_scheduled = False
                            db_session.merge(etl)
                            db_session.commit()
                            etl.etl_not_valid(e)

        except Exception as e:
            logger.exception(e)
            raise Exception(e)

    def sync_delay(self):

        if self.status != EtlStatus.STOPPED:
            message = 'Task Already running'
            logger.warning(message)
            raise Exception(message)

        self.status = EtlStatus.PENDING
        self.is_scheduled = True

        db.session.merge(self)
        db.session.commit()

        self.sync.delay(etl_id=self.id)

        # db_session.merge(etl)
        # db_session.commit()
        #
        # # run celery task
        # sync_etl.delay(etl_id=etl.id)
        #
        #
        # # run celery task
        # # locale Celery tasks
        # from bit.tasks import sync_etl
        # sync_etl.delay(etl_id=self.id)

        # run without celery
        # sync_etl(etl_id=self.id)

        # db_session = app_manager.get_db().session()
        #
        # """ Start New Sync ETL TASK. """
        # logging.info('Try Run Sync {}'.format(
        #     self.sql_table_name
        # ))
        # if self.status == EtlStatus.RUNNING:
        #     raise Exception('Task Already running')
        #
        # self.status = EtlStatus.PENDING
        # db_session.merge(self)
        # db_session.commit()

        # run celery task

        # self.run.delay(etl_id=self.id)

        # run without celery
        # self.run(etl_id=self.id)

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

    def sync_once(self):
        """ For test. """

        # logging.info('Try Run Test Sync {}'.format(self.sql_table_name))

        if self.status == EtlStatus.RUNNING:
            raise Exception('Task Already running')

        connector_type = self.get_connector_type()

        if connector_type == 'SQL':

            logger.info('SQL')

            sql = self.etl_sql()

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
                    for column, value in row.items():
                        add_row.update({str(column): value})
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

        raise 'Cols not found'

    # def valiate_columns(self):
    #     """Validate if exsist columnt in table clause """
    #     self.check_columns()
    #
    # def check_columns(self):
    #     logging.info('Check columns')
    #     logging.info('Get columns for query')
    #
    #     limit = 1

        # if self.table.sql:
            #
            # logging.info("Original sql query")
            # # logging.info(self.table.sql)
            #
            # table_sql = sqlparse.format(
            #     self.table.sql, reindent=True,
            #     keyword_case='upper').strip()
            #
            # statement_sql = sqlparse.parse(table_sql)[0]
            #
            # if statement_sql.get_type() != 'SELECT':
            #     raise Exception('Allow only SELECT STATEMENTS')
            #
            # logging.info("statement_sql is SELECT")
            # new_statement_sql = []
            #
            # for token in statement_sql.tokens:
            #     if token.value in ['ORDER', 'LIMIT']:
            #         break
            #     new_statement_sql.append(str(token))
            #
            # logging.info("Parsed sql query")
            # new_statement_sql = u''.join(new_statement_sql)

            # limit_one = '{} LIMIT {}'.format(
            #     new_statement_sql,
            #     limit
            # )
            # self.get_columns_from_etl_table()
            # r = sqltypes.INTEGER
            # return False
            # logging.info(limit_one)
            # add_rows = []
            # with self.remote_engine.connect() as remote_con:
                # rs = remote_con.execute(limit_one).first()
                # rs = remote_con.execute(limit_one)
                # column_names = ([col[0] for col in cursor.description]
                #                 if cursor.description else [])
                # dialect = rs.context.dialect
                # print(dialect.ischema_names)
                # print(dialect.ischema_names[3])
                # typemap = dialect.dbapi_type_map
                # mapped_type = typemap.get(3, sqltypes.NULLTYPE)
                # if rs:
                #   for idx, rec in enumerate(rs.cursor.description):
                # colname = rec[0]
                # mapped_type = typemap.get(coltype, sqltypes.NULLTYPE)
                # coltype = rec[1]
                # rs = remote_con.execute(limit_one).first()
                # if rs:
                    # for row in rs:
                    #    print(type(row))
                    # for column, value in row.items():
                    #     print(column)
                    #     print(column.type)
                    # pprint(rs.keys())
                    # pprint(rs._metadata.keys)
                    # rss = remote_con.execute(limit_one).scalar()
                    # pprint(rss)
                    # for row in rs:
                    # pprint(dir(row))
                    # add_row = {}
                    # for column, value in row.items():
                    # print(dir(column))
                    # print(dir(value))
                    # add_row.update({str(column): str(value)})
                    # add_rows.append(add_row)
                    # logging.info(add_rows)
        # return False
        # Table 'bit_etl._etl_q' is already defined for this MetaData instance.
        # Specify 'extend_existing=True' to redefine options and columns on
        # an existing Table object.

# TODO WE CAN MOVE TO FULL ACCESS CONTROL ON CREATE SELF PACKAGE
