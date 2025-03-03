"""
@author: Ethan
@contact: email:
@Created on: 2025/1/1 11:26
@Remark:
"""
from django.apps import AppConfig


class DvadminCeleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lelu_admin_test'
    url_prefix = "lelu_admin_test"