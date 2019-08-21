from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from django.db.models import Q
from collections import OrderedDict

from apps.record.models import PushRecord, RechargeRecord, SmsSign, SmsTemplate
from apps.record.serializers import PushRecordSerializer, RechargeRecordSerializer, PushInfoSerializer, \
    BatchPushSerializer, SignSerializer, TemplateSerializer, BatchPushRecordSerializer, SmsTemplateSerializer
from apps.record.filters import PushFilter

from my_utils.my_viewsets import ModelViewSet, GetViewSet, NoUpdateDestroyViewSet
from my_utils.permissions import IsAdminOrReadOnly
from my_utils.pagination import BasePagination
from my_base.base_serializers import SerializerUtil
from my_utils.throttling import WhiteListRateThrottle
from sms_middleground.settings import ACCESS_KEY_ID, ACCESS_KEY_SECRET, SMS_DEBUG



class PushRecordViewSet(NoUpdateDestroyViewSet):
    """
    list:
        获取推送列表
    retrieve:
        通过id获取单个推送
    update:
        更新推送
    partial_update:
        局部更新推送
    destroy:
        删除推送
    create:
        添加推送
    """
    # permission_classes = (IsAdminOrReadOnly,)
    permission_classes = (AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    throttle_classes = (AnonRateThrottle,)
    pagination_class = BasePagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filters.OrderingFilter.ordering_description = '排序参数: id -id'
    filter_class = PushFilter
    # filterset_fields = ('type',)
    search_fields = ('alert', 'secret_key')
    # ordering_fields = ('id',)
    queryset = PushRecord.objects.no_delete_all().order_by('-create_time')
    serializer_class = PushRecordSerializer


class BatchPushRecordViewSet(NoUpdateDestroyViewSet):
    """
    list:
        获取批量推送列表
    retrieve:
        通过id获取单个推送
    update:
        更新批量推送
    partial_update:
        局部更新批量推送
    destroy:
        删除批量推送
    create:
        添加批量推送
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    throttle_classes = (AnonRateThrottle,)
    pagination_class = BasePagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filters.OrderingFilter.ordering_description = '排序参数: id -id'
    filter_class = PushFilter
    # filterset_fields = ('type',)
    search_fields = ('alert', 'secret_key')
    # ordering_fields = ('id',)
    queryset = PushRecord.objects.no_delete_all().order_by('-create_time')
    serializer_class = BatchPushSerializer


class PushInfoViewSet(GetViewSet):
    """
    list:
        获取推送列表
    retrieve:
        通过id获取单个推送
    update:
        更新推送
    partial_update:
        局部更新推送
    destroy:
        删除推送
    create:
        添加推送
    """
    # permission_classes = (IsAdminOrReadOnly,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # pagination_class = BasePagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filters.OrderingFilter.ordering_description = '排序参数: id -id'
    filter_class = PushFilter
    # filterset_fields = ('type',)
    # search_fields = ('alert', 'secret_key')
    # ordering_fields = ('id',)
    queryset = PushRecord.objects.no_delete_all().order_by('-create_time')
    serializer_class = PushInfoSerializer


class PushInfoByUserViewSet(ModelViewSet):
    """
    list:
        获取推送列表
    retrieve:
        通过id获取单个推送
    update:
        更新推送
    partial_update:
        局部更新推送
    destroy:
        删除推送
    create:
        添加推送
    """
    # permission_classes = (IsAdminOrReadOnly,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    pagination_class = BasePagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filters.OrderingFilter.ordering_description = '排序参数: id -id'
    filter_class = PushFilter
    # filterset_fields = ('type',)
    search_fields = ('alert', 'secret_key', 'mobile')
    # ordering_fields = ('id',)
    # queryset = PushRecord.objects.no_delete_all().order_by('-create_time')
    serializer_class = PushInfoSerializer

    def get_queryset(self):
        return PushRecord.objects.no_delete_all().filter(Q(client__user=self.request.user), ~Q(mobile='batch')).order_by('-create_time')


class RechargeRecordViewSet(NoUpdateDestroyViewSet):
    """
    list:
        获取充值列表
    retrieve:
        通过id获取单个充值
    update:
        更新充值
    partial_update:
        局部更新充值
    destroy:
        删除充值
    create:
        添加充值
    """
    # permission_classes = (IsAdminOrReadOnly,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    pagination_class = BasePagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filters.OrderingFilter.ordering_description = '排序参数: id -id'
    # filter_class = RecordFilter
    # filterset_fields = ('type',)
    search_fields = ('client__name', 'client__company')
    # ordering_fields = ('id',)
    queryset = RechargeRecord.objects.no_delete_all().order_by('-create_time')
    serializer_class = RechargeRecordSerializer


class SignViewSet(ModelViewSet):
    """
    list:
        获取签名
    retrieve:
        通过id获取单个签名
    update:
        更新签名
    partial_update:
        局部更新签名
    destroy:
        删除签名
    create:
        添加签名
    """
    # permission_classes = (IsAdminOrReadOnly,)
    permission_classes = (AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    pagination_class = BasePagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filters.OrderingFilter.ordering_description = '排序参数: id -id'
    # filter_class = PushFilter
    # filterset_fields = ('type',)
    # search_fields = ('alert', 'secret_key', 'mobile')
    # ordering_fields = ('id',)
    queryset = SmsSign.objects.no_delete_all().order_by('-create_time')
    serializer_class = SignSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sign_status==0:
            return Response(OrderedDict({'message': '不支持删除审核中的签名'}), status=status.HTTP_400_BAD_REQUEST)
        else:
            # 获取客户信息
            _client = instance.client
            # 获取客户保存的阿里账号AccessKeyId
            # 获取客户保存的阿里账号AccessKeySecret
            if _client.access_key_id:
                _access_key_id = _client.access_key_id
                _access_key_secret = _client.access_key_secret
            else:
                _access_key_id = ACCESS_KEY_ID
                _access_key_secret = ACCESS_KEY_SECRET
            # 获取签名名称
            _sign_name = instance.sign_name
            # 创建短信对象
            from my_sms.sms import AliSms
            import json
            sms = AliSms(_access_key_id, _access_key_secret)
            # 是否非测试环境
            if not SMS_DEBUG:
                # 发送删除请求
                result = sms.delete_sms_sign(_sign_name)
                # 保存平台返回的报文
                _res_json = json.loads(result)
                # 消息发送结果判断
                if _res_json['Code'] == 'OK':
                    self.perform_destroy(instance)
                    return Response('', status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response(_res_json, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(OrderedDict({'message': '测试环境不执行删除操作'}), status=status.HTTP_204_NO_CONTENT)


class TemplateViewSet(ModelViewSet):
    """
    list:
        获取推送模板
    retrieve:
        通过id获取单个模板
    update:
        更新模板
    partial_update:
        局部更新模板
    destroy:
        删除模板
    create:
        添加模板
    """
    # permission_classes = (IsAdminOrReadOnly,)
    permission_classes = (AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    pagination_class = BasePagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filters.OrderingFilter.ordering_description = '排序参数: id -id'
    # filter_class = PushFilter
    # filterset_fields = ('type',)
    # search_fields = ('alert', 'secret_key', 'mobile')
    # ordering_fields = ('id',)
    queryset = SmsTemplate.objects.no_delete_all().order_by('-create_time')
    serializer_class = TemplateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.template_status==0:
            return Response(OrderedDict({'message': '不支持删除审核中的模板'}), status=status.HTTP_400_BAD_REQUEST)
        else:
            # 获取客户信息
            _client = instance.client
            # 获取客户保存的阿里账号AccessKeyId
            # 获取客户保存的阿里账号AccessKeySecret
            if _client.access_key_id:
                _access_key_id = _client.access_key_id
                _access_key_secret = _client.access_key_secret
            else:
                _access_key_id = ACCESS_KEY_ID
                _access_key_secret = ACCESS_KEY_SECRET
            # 获取模板code
            _template_code = instance.template_code
            # 创建短信对象
            from my_sms.sms import AliSms
            import json
            sms = AliSms(_access_key_id, _access_key_secret)
            # 是否非测试环境
            if not SMS_DEBUG:
                # 发送删除请求
                result = sms.delete_sms_template(_template_code)
                # 保存平台返回的报文
                _res_json = json.loads(result)
                # 消息发送结果判断
                if _res_json['Code'] == 'OK':
                    self.perform_destroy(instance)
                    return Response('', status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response(_res_json, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(OrderedDict({'message': '测试环境不执行删除操作'}), status=status.HTTP_204_NO_CONTENT)



class BatchPushRecordViewSet2(viewsets.ModelViewSet):
    '''批量推送'''
    permission_classes = (AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    throttle_classes = (AnonRateThrottle,)
    pagination_class = BasePagination
    filter_class = PushFilter
    search_fields = ('alert', 'secret_key')
    queryset = PushRecord.objects.no_delete_all().order_by('-create_time')
    serializer_class = BatchPushRecordSerializer



class SmsTemplateViewSet(ModelViewSet):
    '''短信模板'''
    permission_classes = (AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    pagination_class = BasePagination
    queryset = SmsTemplate.objects.no_delete_all().order_by('-create_time')
    serializer_class = SmsTemplateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.template_status==0:
            return Response(OrderedDict({'message': '不支持删除审核中的模板'}), status=status.HTTP_400_BAD_REQUEST)
        else:
            # 获取客户信息
            _client = instance.client
            # 获取客户保存的阿里账号AccessKeyId
            # 获取客户保存的阿里账号AccessKeySecret
            if _client.access_key_id:
                _access_key_id = _client.access_key_id
                _access_key_secret = _client.access_key_secret
            else:
                _access_key_id = ACCESS_KEY_ID
                _access_key_secret = ACCESS_KEY_SECRET
            # 获取模板code
            _template_code = instance.template_code
            # 创建短信对象
            from my_sms.sms import AliSms
            import json
            sms = AliSms(_access_key_id, _access_key_secret)
            # 是否非测试环境
            if not SMS_DEBUG:
                # 发送删除请求
                result = sms.delete_sms_template(_template_code)
                # 保存平台返回的报文
                _res_json = json.loads(result)
                # 消息发送结果判断
                if _res_json['Code'] == 'OK':
                    self.perform_destroy(instance)
                    return Response('', status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response(_res_json, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(OrderedDict({'message': '测试环境不执行删除操作'}), status=status.HTTP_204_NO_CONTENT)




