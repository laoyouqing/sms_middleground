from django.db import models
from django.contrib.auth.models import AbstractUser

from my_base.base_model import BaseModel
from my_utils import enum


# Create your models here.
class User(AbstractUser, BaseModel):
    """
    用户
    """
    username = models.CharField(max_length=150, unique=True, verbose_name='用户名', help_text='最大长度150字符')
    password = models.CharField(max_length=128, verbose_name='密码', help_text='最大长度128字符')
    name = models.CharField(max_length=30, verbose_name='姓名', help_text='最大长度30字符')
    gender = models.CharField(max_length=6, choices=enum.GENDER, default='male', verbose_name='性别',
                              help_text='male：男 female：女')
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name='电话号码', help_text='合法11位手机号码')
    email = models.CharField(max_length=320, blank=True, null=True, verbose_name='电子邮箱', help_text='合法电子邮箱')
    birthday = models.DateField(null=True, blank=True, verbose_name='生日', help_text='生日')

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name if self.name else self.username


class Client(BaseModel):
    """
    客户表
    """
    name = models.CharField(max_length=30, unique=True, verbose_name='姓名', help_text='最大长度30字符')
    mobile = models.CharField(max_length=11, verbose_name='电话号码', help_text='余额不足提醒时就收短信号码')
    push_num = models.IntegerField(default=0, verbose_name='可推送次数', help_text='消息推送可用次数')
    pushed_num = models.IntegerField(default=0, verbose_name='已推送次数', help_text='消息推送已经使用次数')
    warn_limit = models.IntegerField(default=0, verbose_name='预警界限', help_text='达到给界限将发送充值提醒')
    access_key_id = models.CharField(max_length=30, blank=True, null=True, verbose_name='AccessKeyId',
                                     help_text='阿里账号AccessKeyId')
    access_key_secret = models.CharField(max_length=30, blank=True, null=True, verbose_name='AccessKeySecret',
                                         help_text='阿里账号AccessKeySecret')
    sign_name = models.CharField(max_length=30, verbose_name='短信签名', help_text='阿里短信签名')
    secret_key = models.CharField(max_length=36, unique=True, verbose_name='密钥', help_text='消息推送验证标识')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name='账号',
                               help_text='账号', related_name='client')

    class Meta:
        db_table = 'client'
        verbose_name = '客户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


U_C_LIST = [User, Client]
