from django.db import models

from cachetask.managers import CacheManager, GreedyCacheManager



class MyBaseModel(models.Model):
    name = models.CharField(max_length=25)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class MyModel(MyBaseModel):
    # Enables selective cached queries
    objects = CacheManager()

class MyGreedyModel(MyBaseModel):
    """
    Every query is cached
    Every cache is great
    If a cache is missed
    Sysadmin gets quite irate
    """
    objects = GreedyCacheManager()
