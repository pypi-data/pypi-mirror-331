"""
@author: Ethan
@contact: email:
@Created on: 2025/1/1 11:49
@Remark:
"""
from application import settings

# ================================================= #
# ***************** 插件配置区开始 *******************
# ================================================= #
# 路由配置
plugins_url_patterns = [
    {"re_path": r'api/plugins/', "include": "lelu_admin_test.urls"}
]
# 租户模式中，public模式共享app配置
tenant_shared_apps = []
# app 配置
apps = ['lelu_admin_test']

settings.INSTALLED_APPS += [app for app in apps if app not in settings.INSTALLED_APPS]
settings.TENANT_SHARED_APPS += tenant_shared_apps

# ********** 注册路由 **********
settings.PLUGINS_URL_PATTERNS += plugins_url_patterns

# 避免时区的问题
CELERY_ENABLE_UTC = False
DJANGO_CELERY_BEAT_TZ_AWARE = False
