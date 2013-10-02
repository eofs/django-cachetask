from celery.task import task
from celery.utils.log import get_task_logger

from cachetask.utils import import_from_string


logger = get_task_logger(__name__)


@task()
def refresh_cache(klass_str, obj_args, obj_kwargs, call_args, call_kwargs):
    try:
        klass = import_from_string(klass_str)
    except ImportError:
        return

    # Call refresh to update the cache
    obj = klass(*obj_args, **obj_kwargs)
    obj.refresh(*call_args, **call_kwargs)
