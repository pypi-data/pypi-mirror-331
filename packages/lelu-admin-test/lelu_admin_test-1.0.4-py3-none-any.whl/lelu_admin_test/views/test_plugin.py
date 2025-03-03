"""
@author: Ethan
@contact: email:
@Created on: 2025/1/1 11:51
@Remark:
"""
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from ..models import *


class TestPluginSerializer(CustomModelSerializer):
    """
    Plugin - 序列化器
    """

    class Meta:
        model = TestPlugin
        fields = "__all__"
        read_only_fields = ["id"]


class TestPluginViewSet(CustomModelViewSet):
    """
    插件测试
    """
    queryset = TestPlugin.objects.all()
    serializer_class = TestPluginSerializer
    permission_classes = []
