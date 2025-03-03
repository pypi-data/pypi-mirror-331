"""
@author: Ethan
@contact: email:
@Created on: 2025/1/1 11:55
@Remark:
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TestPlugin(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    remark = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "test_plugin"
        verbose_name = _('Test Plugin')
        verbose_name_plural = _('Test Plugin')
