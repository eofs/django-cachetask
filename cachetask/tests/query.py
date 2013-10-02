from django.test import TestCase
from django.core.cache import cache

from cachetask.base import CacheTask
from cachetask.tests.testapp.models import MyModel, MyGreedyModel


class MyTask(CacheTask):
    called_async = False

    def run(self):
        return [1, 2, 3]

    def async_refresh(self, *args, **kwargs):
        self.called_async = True
        super(MyTask, self).async_refresh(*args, **kwargs)


class CacheBaseCase(TestCase):
    def setUp(self):
        MyModel.objects.create(name='Bob')
        MyModel.objects.create(name='Alice')
        MyGreedyModel.objects.create(name='Bob')
        MyGreedyModel.objects.create(name='Alice')

    def tearDown(self):
        MyModel.objects.all().delete()
        MyGreedyModel.objects.all().delete()
        cache.clear()


class QueryTestCase(CacheBaseCase):
    def test_one_get_call(self):
        """
        First call should return value
        """
        bob = MyModel.objects.cached().get(name='Bob')
        self.assertEqual('Bob', bob.name)

    def test_multiple_get_calls(self):
        """
        Multiple calls should only trigger one database query to execute
        """
        with self.assertNumQueries(1):
            for _ in xrange(10):
                MyModel.objects.cached().get(name='Bob')

    def test_one_filter_call(self):
        """
        Filtered query should return value
        """
        results = MyModel.objects.cached().filter(name='Bob')
        self.assertEqual(1, len(results))
        self.assertEqual('Bob', results[0].name)

    def test_multiple_filter_calls(self):
        """
        Multiple calls to filtered query should only trigger one database query to execute
        """
        with self.assertNumQueries(1):
            for _ in xrange(10):
                results = MyModel.objects.cached().filter(name='Bob')
                self.assertEqual(1, len(results))

class GreedyQueryTestCase(CacheBaseCase):
    def test_one_filter_call(self):
        """
        Filtered query should return value
        """
        results = MyGreedyModel.objects.cached().filter(name='Bob')
        self.assertEqual(1, len(results))
        self.assertEqual('Bob', results[0].name)

    def test_multiple_filter_calls(self):
        """
        Multiple calls to filtered query should only trigger one database query to execute
        """
        with self.assertNumQueries(1):
            for _ in xrange(10):
                results = MyGreedyModel.objects.filter(name='Bob')
                self.assertEqual(1, len(results))
                self.assertEqual('Bob', results[0].name)
