from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.user.serializers import UserSerializer, ClientSerializer, BalanceSerializer
from apps.user.models import Client

from my_utils import mixins
from my_utils.my_viewsets import ModelViewSet, NoDestroyViewSet, GetViewSet
from my_utils.pagination import BasePagination
from my_utils.permissions import IsAdminOrReadOnly
from my_base.base_serializers import SerializerUtil

User = get_user_model()


class CustomBackend(ModelBackend):
    """
    自定义用户验证
    """

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class UserViewSet(NoDestroyViewSet):
    """
    list:
        获取用户列表
    retrieve:
        通过id获取单个用户
    update:
        更新用户
    partial_update:
        局部更新用户
    destroy:
        删除用户
    create:
        添加用户
    """
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    pagination_class = BasePagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filters.OrderingFilter.ordering_description = '排序参数: id -id'
    # filter_class =
    # filterset_fields = ('', )
    search_fields = ('name', 'username')
    # ordering_fields = ('id',)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ClientViewSet(NoDestroyViewSet):
    """
    list:
        获取客户列表
    retrieve:
        通过id获取单个客户
    update:
        更新客户
    partial_update:
        局部更新客户
    destroy:
        删除客户
    create:
        添加客户
    """
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    pagination_class = BasePagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filters.OrderingFilter.ordering_description = '排序参数: id -id'
    # filter_class =
    # filterset_fields = ('', )
    search_fields = ('name',)
    # ordering_fields = ('id',)
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ClientInfoViewSet(GetViewSet):
    """
    list:
        获取客户列表
    retrieve:
        通过id获取单个客户
    update:
        更新客户
    partial_update:
        局部更新客户
    destroy:
        删除客户
    create:
        添加客户
    """
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # pagination_class = BasePagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filters.OrderingFilter.ordering_description = '排序参数: id -id'
    # filter_class =
    # filterset_fields = ('', )
    # search_fields = ('name',)
    # ordering_fields = ('id',)
    queryset = Client.objects.all()
    serializer_class = ClientSerializer




class BalanceViewSet(mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''查询可推送次数'''
    # permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    queryset = Client.objects.all()
    lookup_field = 'secret_key'
    serializer_class = BalanceSerializer
