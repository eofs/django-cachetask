import pickle
import hashlib

from django.db import models

from cachetask.base import CacheTask


class CacheQuerySet(models.query.QuerySet):
    def get(self, *args, **kwargs):
        qs = self.filter(*args, **kwargs)
        p_query = pickle.dumps(qs.query)
        return QueryGetTask().get(self.model, p_query)
        #return super(CacheQuerySet, self).get(*args, **kwargs)

    def __len__(self):
        p_query = pickle.dumps(self.query)
        return QueryLenTask().get(self.model, p_query)

    def _get_hash(self, query):
        """
        Calculate SHA1 hash for the query using its string representation
        """
        return hashlib.sha1(str(query)).hexdigest()


class QueryGetTask(CacheTask):
    """
    Cache task to run the query in background worker.
    """
    def run(self, model, pickled_query):
        # Create a fake query
        qs = model.objects.all()
        # Restore original query
        qs.query = pickle.loads(pickled_query)
        return qs.get()


class QueryLenTask(CacheTask):
    """
    Cache task to run the query in background worker.
    """
    def run(self, model, pickled_query):
        # Create a fake query
        qs = model.objects.all()
        # Restore original query
        qs.query = pickle.loads(pickled_query)
        return len(qs)
