from django.db import models
from django.contrib.auth.models import AbstractUser

from my_base.base_model import BaseModel
from apps.user.models import Client, User
from my_utils import enum


class SmsSign(BaseModel):
    """
    短信签名
    """
    sign_name = models.CharField(max_length=30, verbose_name='签名名称', help_text='签名名称')
    sign_source = models.SmallIntegerField(choices=enum.SIGN_SOURCE, verbose_name='签名来源',
                                           help_text='0：企事业单位的全称或简称。1：工信部备案网站的全称或简称。2：APP应用的全称或简称。3：公众号或小程序的全称或简称。4：电商平台店铺名的全称或简称。5：商标名的全称或简称')
    remark = models.CharField(max_length=30, verbose_name='申请说明',
                              help_text='请在申请说明中详细描述您的业务使用场景，申请工信部备案网站的全称或简称请在此处填写域名，长度不超过200个字符')
    action = models.CharField(blank=True, null=True, max_length=30, verbose_name='系统规定参数', help_text='系统规定参数')
    access_key_id = models.CharField(blank=True, null=True, max_length=30, verbose_name='AccessKeyId',
                                     help_text='阿里主账号AccessKey的ID')
    file_suffix = models.ImageField(blank=True, null=True, upload_to='sign', verbose_name='签名证明',
                                    help_text='签名的证明文件格式，支持上传多张图片。当前支持jpg、png、gif或jpeg格式的图片。个别场景下，申请签名需要上传证明文件。')
    file_contents = models.ImageField(blank=True, null=True, upload_to='sign', verbose_name='签名质证明文件',
                                      help_text='签名的质证明文件经base64编码后的字符串。图片不超过2 MB。个别场景下，申请签名需要上传证明文件。')
    sign_status = models.SmallIntegerField(choices=enum.TEMPLATE_STATUS, default=0, verbose_name='申请状态',
                                               help_text='0：审核中。1：审核通过。2：审核失败，请在返回参数Reason中查看审核失败原因。')
    reason = models.CharField(blank=True, null=True, max_length=300, verbose_name='审核备注', help_text='审核不通过具体原因')
    result = models.CharField(max_length=30, choices=enum.RESULT, blank=True, null=True, verbose_name='推送结果',
                              help_text='success: 成功, fail: 失败, error: 错误')
    response_message = models.CharField(max_length=300, blank=True, null=True, verbose_name='返回报文',
                                        help_text='服务平台返回的报文数据')
    secret_key = models.CharField(blank=True, null=True, max_length=36, verbose_name='密钥', help_text='客户注册时生成的唯一密匙')
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name='所属客户',
                               help_text='所属客户', related_name='my_sign')

    class Meta:
        db_table = 'sms_sign'
        verbose_name = '短信签名'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s(%s)' % (self.sign_name, self.client.name if self.client else '')


class SmsTemplate(BaseModel):
    """
    短信模板
    """
    template_type = models.SmallIntegerField(choices=enum.TEMPLATE_TPYE, verbose_name='短信类型',
                                             help_text='0：验证码。1：短信通知。2：推广短信。3：国际/港澳台消息。')
    template_name = models.CharField(max_length=30, verbose_name='模板名称', help_text='长度为1~30个字符')
    template_content = models.CharField(max_length=500, verbose_name='模板内容', help_text='长度为1~500个字符')
    template_code = models.CharField(blank=True, null=True, max_length=30, verbose_name='模板编号', help_text='阿里短信模板编号')
    template_status = models.SmallIntegerField(choices=enum.TEMPLATE_STATUS, default=0, verbose_name='申请状态',
                                               help_text='0：审核中。1：审核通过。2：审核失败，请在返回参数Reason中查看审核失败原因。')
    reason = models.CharField(blank=True, null=True, max_length=300, verbose_name='审核备注', help_text='审核不通过具体原因')
    remark = models.CharField(max_length=100, verbose_name='申请说明', help_text='请在申请说明中描述您的业务使用场景，长度为1~100个字符。')
    action = models.CharField(blank=True, null=True, max_length=30, verbose_name='系统规定参数', help_text='系统规定参数')
    access_key_id = models.CharField(blank=True, null=True, max_length=30, verbose_name='AccessKeyId',
                                     help_text='阿里主账号AccessKey的ID')
    result = models.CharField(max_length=30, choices=enum.RESULT, blank=True, null=True, verbose_name='推送结果',
                              help_text='success: 成功, fail: 失败, error: 错误')
    response_message = models.CharField(max_length=300, blank=True, null=True, verbose_name='返回报文',
                                        help_text='服务平台返回的报文数据')
    secret_key = models.CharField(blank=True, null=True, max_length=36, verbose_name='密钥', help_text='客户注册时生成的唯一密匙')
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name='所属客户',
                               help_text='所属客户', related_name='my_template')

    class Meta:
        db_table = 'sms_template'
        verbose_name = '短信模板'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s(%s)' % (self.template_name, self.client.name if self.client else '')


class PushRecord(BaseModel):
    """
    短信记录
    """
    mobile = models.CharField(max_length=11, verbose_name='电话号码', help_text='要接收短信的号码')
    mobile_file = models.FileField(blank=True, null=True, upload_to='mobile', verbose_name='电话号码文件',
                                   help_text='要接收短信的号码文件')
    msg = models.CharField(max_length=1000, verbose_name='短信内容', help_text='短信内容')
    template_code = models.CharField(max_length=30, verbose_name='短信模板id', help_text='阿里云短信模板id')
    sign_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='短信签名', help_text='短信签名')
    result = models.CharField(max_length=30, choices=enum.RESULT, blank=True, null=True, verbose_name='推送结果',
                              help_text='success: 成功, fail: 失败, error: 错误')
    response_message = models.CharField(max_length=300, blank=True, null=True, verbose_name='返回报文',
                                        help_text='服务平台返回的报文数据')
    secret_key = models.CharField(max_length=36, verbose_name='密钥', help_text='客户注册时生成的唯一密匙')
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name='所属客户',
                               help_text='所属客户', related_name='my_push')

    # create_time = models.DateTimeField(verbose_name='创建时间', help_text='精确到秒')  # 模拟数据使用

    class Meta:
        db_table = 'push_record'
        verbose_name = '短信记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.client.name if self.client else ''


class RechargeRecord(BaseModel):
    """
    充值记录
    """
    recharge_num = models.IntegerField(default=0, verbose_name='充值数量', help_text='充值消息推送可用次数')
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name='所属客户',
                               help_text='被充值客户', related_name='recharge')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name='操作人',
                             help_text='提交操作人员', related_name='my_recharge')

    class Meta:
        db_table = 'recharge_record'
        verbose_name = '充值记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%(client)s(操作人: %(user)s)' % {'client': self.client.name, 'user': self.user.name}


R_C_LIST = [SmsTemplate, SmsSign, PushRecord, RechargeRecord]
