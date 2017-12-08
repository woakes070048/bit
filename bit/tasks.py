# system
from logging import getLogger
from datetime import datetime
from celery import shared_task

# superset
from superset import app
from superset.utils import get_celery_app

# locale
from bitstart import app_manager
from bit.models import EtlTable
from bit.utils.etl_status import EtlStatus


logger = getLogger(__name__)

celery_app = get_celery_app(app.config)


@shared_task
def run_etl():

    logger.info('Sheduler try run etl tasks')

    db_session = app_manager.get_db().session()

    # TODO add lock table
    etls = db_session.query(EtlTable).filter_by(
        is_active=True,
        is_valid=True,
        is_scheduled=False
    ).filter(
        EtlTable.sync_periodic != 0,
        EtlTable.sync_next_time < datetime.utcnow()
    ).update({'is_scheduled': True}, synchronize_session='fetch')

    for etl in etls:
        etl.sync_delay()

        # if etl.status == EtlStatus.RUNNING:
        #     message = 'Task Already running'
        #     logger.exception(message)
        #     raise Exception(message)
        #
        # etl.status = EtlStatus.PENDING
        # etl.is_scheduled = True
        #
        # db_session.merge(etl)
        # db_session.commit()
        #
        # # run celery task
        # sync_etl.delay(etl_id=etl.id)

    return True

#
# @celery_app.task(ignore_results=True)
# def sync_etl(etl_id=0):
#     """Run Etl Sync Data From DataSource to DWH."""
#
#     logger.info('Run Etl Sync')
#
#     db_session = app_manager.get_db().session()
#
#     try:
#         etl = db_session.query(EtlTable).filter_by(id=etl_id).one()
#     except Exception as e:
#         logger.exception(e)
