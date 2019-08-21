"""sms_middleground URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import xadmin
from django.conf.urls import url, include
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework.routers import DefaultRouter

from sms_middleground.settings import MEDIA_ROOT
from apps.user.views import UserViewSet, ClientViewSet, ClientInfoViewSet, BalanceViewSet
from apps.record.views import PushRecordViewSet, RechargeRecordViewSet, PushInfoViewSet, BatchPushRecordViewSet, \
    PushInfoByUserViewSet, TemplateViewSet, SignViewSet, BatchPushRecordViewSet2, SmsTemplateViewSet
from apps.report.views import ReportViewSet

router = DefaultRouter()

router.register(r'user', UserViewSet, basename='user')  # 用户
router.register(r'client', ClientViewSet, basename='client')  # 客户
router.register(r'client_info', ClientInfoViewSet, basename='client_info')  # 客户不分页

router.register(r'push', PushRecordViewSet, basename='push')  # 推送
router.register(r'batch_push', BatchPushRecordViewSet, basename='batch_push')  # 批量推送
router.register(r'self_push', PushInfoByUserViewSet, basename='self_push')  # 个人推送
router.register(r'push_info', PushInfoViewSet, basename='push_info')  # 推送不分页
router.register(r'recharge', RechargeRecordViewSet, basename='recharge')  # 充值
router.register(r'sign', SignViewSet, basename='sign')  # 签名
router.register(r'template', TemplateViewSet, basename='template')  # 模板

router.register(r'report', ReportViewSet, basename='report')  # 统计

router.register(r'batch', BatchPushRecordViewSet2, basename='batch')  #批量
router.register(r'smstemplate', SmsTemplateViewSet, basename='smstemplate')  #sms模板
router.register(r'balance', BalanceViewSet, basename='balance')  #可推送次数

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),  # 后台管理界面
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),  # DRF
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),  # 访问图片
    url(r'^docs/', include_docs_urls(title='短信中台管理')),  # 接口文档
    url(r'^login/', obtain_jwt_token, name='login'),  # jwt
    url(r'^refresh/', refresh_jwt_token, name='refresh'),  # jwt 刷新

    url(r'^', include(router.urls)),
]
