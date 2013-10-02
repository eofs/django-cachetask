from django.test import TestCase
from django.core.cache import cache

from cachetask.base import CacheTask


class MyTask(CacheTask):
    called_async = False

    def run(self):
        return [1, 2, 3]

    def async_refresh(self, *args, **kwargs):
        self.called_async = True
        super(MyTask, self).async_refresh(*args, **kwargs)

class CacheBaseCase(TestCase):
    def setUp(self):
        self.task = MyTask()

    def tearDown(self):
        cache.clear()


class CacheTaskTests(CacheBaseCase):
    def test_first_call(self):
        """
        First call should run code synchronously
        """
        self.assertEqual([1 ,2, 3], self.task.get())

    def test_second_call(self):
        """
        Second call should also get value
        """
        self.assertEqual([1 ,2, 3], self.task.get())
        self.assertEqual([1 ,2, 3], self.task.get())
