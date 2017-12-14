# system
from logging import getLogger
from datetime import datetime
from celery import shared_task

# superset
from superset import db
from superset import app
from superset.utils import get_celery_app

# locale
from bitstart import app_manager
from bit.models import EtlTable


celery_app = get_celery_app(app)
logger = getLogger(__name__)

from celery.signals import worker_process_init


@worker_process_init.connect
def on_fork_close_session(**kwargs):
    if db.session is not None:
        db.session.close()
        db.engine.dispose()


# @shared_task
@celery_app.task(ignore_results=True)
def run_etl():

    # db_session = app_manager.get_db().session()
    db_session = db.session()

    msg = 'Scheduler Try Run ETL Async Tasks'
    print(msg)
    logger.info(msg)

    etl_tasks = db_session.query(EtlTable).with_for_update(
        skip_locked=True
    ).filter(
        EtlTable.is_active.is_(True),
        EtlTable.is_valid.is_(True),
        EtlTable.is_scheduled.isnot(True),
        EtlTable.sync_periodic != 0,
        EtlTable.sync_next_time < datetime.utcnow()
    )

    for etl_task in etl_tasks:
        etl_task.is_scheduled = True
        logger.info(etl_task)
        db_session.merge(etl_task)
        async_etl.delay(etl_id=etl_task.id)
    db_session.commit()
    return True


@celery_app.task(ignore_results=True)
def async_etl(etl_id=0):
    """Run Etl Sync Data From DataSource to DWH."""

    msq = 'Run Async ETL Id ({}) Task'.format(etl_id)
    print(msq)
    logger.info(msq)

    # db_session = app_manager.get_db().session()
    db_session = db.session()
    try:
        db_session.query(EtlTable).filter_by(id=etl_id).one().sync()
    except Exception as e:
        print(e)
        logger.exception(e)
        raise
