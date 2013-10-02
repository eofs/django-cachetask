from celery.task import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@task()
def refresh_cache(call_args, call_kwargs):
    print 'Hello world!'
