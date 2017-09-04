import logging
from datetime import datetime
from celery import shared_task

# superset
from superset import db

# locale
from bit.models import EtlTable


@shared_task
def run_etl():

    print('run_etl')

    """TODO add lock table"""
    etls = db.session.query(EtlTable).filter_by(
        is_active=True,
        is_valid=True,
        is_scheduled=False
    ).filter(
        EtlTable.sync_periodic != 0,
        EtlTable.sync_next_time < datetime.utcnow()
    )
    # .update({'is_scheduled': True}, synchronize_session='fetch')

    # logging.info(etls.count())
    for etl in etls:
        etl.sync()
        etl.is_scheduled = True
        db.session.merge(etl)
        db.session.commit()
        # logging.info(etl)

    # logging.info('add async task call')
    return True
