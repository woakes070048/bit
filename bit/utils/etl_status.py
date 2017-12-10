class EtlStatus(object):

    """Enum-type class for ETL statuses"""

    STOPPED = 'stopped'
    FAILED = 'failed'
    PENDING = 'pending'
    RUNNING = 'running'
    SCHEDULED = 'scheduled'
    SUCCESS = 'success'
    TIMED_OUT = 'timed_out'
