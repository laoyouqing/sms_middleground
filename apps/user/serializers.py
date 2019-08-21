# coding=utf-8
import re, json, uuid, time
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.validators import UniqueValidator
from django.db import transaction

from apps.user.models import User, Client
from my_base.base_serializers import MyBaseSerializer, SerializerUtil
from my_utils import enum, utils


class UserSerializer(serializers.ModelSerializer, MyBaseSerializer):
    """
    用户
    """
    # username = serializers.CharField(required=True,
    #                                  validators=[UniqueValidator(queryset=User.objects.all(), message="用户名已经存在")],
    #                                  **SerializerUtil.get_serializer_item('username', User))
    # password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True,
    #                                  **SerializerUtil.get_serializer_item('password', User))

    def validate_mobile(self, data):
        if not utils.validate_mobile(data): serializers.ValidationError('电话号码不合法')
        return data

    def validate_email(self, data):
        if not utils.validate_email(data): serializers.ValidationError('电子邮箱不合法')
        return data

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super(UserSerializer, self).update(instance, validated_data)
        if 'password' in validated_data.keys():
            user.set_password(validated_data["password"])
            user.save()
        return user

    class Meta:
        # 模型
        model = User
        # 序列化字段
        fields = '__all__'
        # 级联层级
        depth = 0
        # 只读字段
        read_only_fields = ('create_time', 'update_time', 'is_delete',  # 公共字段
                            'last_login', 'is_superuser', 'first_name', 'last_name', 'date_joined', 'groups',
                            'user_permissions', 'is_staff', 'is_active')
        # 而外参数
        extra_kwargs = SerializerUtil.get_extra_kwargs(model=model, read_only_fields=read_only_fields,
                                                       write_only_fields=('password'),
                                                       validators={
                                                           'username': [UniqueValidator(queryset=User.objects.all(),
                                                                                    message='用户名已经存在')]
                                                       },
                                                       style={
                                                           'password': {'input_type': 'password'}
                                                       }
                                                       )


class ClientSerializer(serializers.ModelSerializer, MyBaseSerializer):
    """
    客户
    """

    def create(self, validated_data):
        _name = validated_data['name']
        # 自动生成密钥
        validated_data['secret_key'] = uuid.uuid5(uuid.NAMESPACE_DNS, '%s-%d' % (_name, int(time.time())))
        # 重置可使用次数
        validated_data['push_num'] = 100
        # 重置已使用次数
        validated_data['pushed_num'] = 0
        instance = super().create(validated_data)
        return instance

    class Meta:
        # 模型
        model = Client
        # 序列化字段
        fields = '__all__'
        # 级联层级
        depth = 0
        # 只读字段
        read_only_fields = ('create_time', 'update_time', 'is_delete',  # 公共字段
                            'secret_key', 'pushed_num')
        # 而外参数
        extra_kwargs = SerializerUtil.get_extra_kwargs(model=model, read_only_fields=read_only_fields,
                                                       validators={'name': [UniqueValidator(queryset=Client.objects.all(),
                                                                                            message='客户已被注册')]})




class BalanceSerializer(serializers.ModelSerializer):
    '''查询可推送次数'''

    class Meta:
        # 模型
        model = Client
        fields=('push_num',)
