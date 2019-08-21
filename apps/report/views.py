from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
# from rest_framework.throttling import UserRateThrottle
from rest_framework import status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.report.models import Report
from apps.report.serializers import ReportSerializer
# from apps.record.filters import PushFilter

from my_utils.my_viewsets import ModelViewSet, GetViewSet, NoUpdateViewSet
from my_utils.permissions import IsAdminOrReadOnly
from my_utils.pagination import BasePagination
from my_base.base_serializers import SerializerUtil
from my_utils.utils import my_response_data
from my_utils.filters import MySearchFilter


class ReportViewSet(NoUpdateViewSet):
    """
    list:
        获取统计列表
    retrieve:
        通过id获取单个统计
    update:
        更新统计
    partial_update:
        局部更新统计
    destroy:
        删除统计
    create:
        添加统计
    """
    # permission_classes = (IsAdminOrReadOnly,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # pagination_class = BasePagination
    filter_backends = (DjangoFilterBackend, MySearchFilter, OrderingFilter)
    # filters.OrderingFilter.ordering_description = '排序参数: id -id'
    # filter_class = Report
    filterset_fields = ('date',)
    # search_fields = ('name',)
    ordering_fields = ('date',)
    queryset = Report.objects.no_delete_all()
    serializer_class = ReportSerializer
