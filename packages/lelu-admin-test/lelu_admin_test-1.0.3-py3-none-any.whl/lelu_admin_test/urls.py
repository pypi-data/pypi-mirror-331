"""
@author: Ethan
@contact: email:
@Created on: 2025/1/1 11:51
@Remark:
"""
from rest_framework import routers
from .views.test_plugin import TestPluginViewSet

router = routers.SimpleRouter()
router.register(r'test_plugin', TestPluginViewSet, basename='test_plugin')
urlpatterns = []
urlpatterns += router.urls
