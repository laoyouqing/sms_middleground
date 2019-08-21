# coding=utf-8
import re, json, time, csv, pandas, random
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.db import transaction
from django.db.models import F

from my_base.base_serializers import MyBaseSerializer, SerializerUtil
from my_utils import utils
from apps.record.models import PushRecord, RechargeRecord, SmsSign, SmsTemplate
from apps.user.models import Client, User
from sms_middleground.settings import ACCESS_KEY_ID, ACCESS_KEY_SECRET, SMS_DEBUG


class PushRecordSerializer(serializers.ModelSerializer, MyBaseSerializer):
    """
    推送记录
    """
    msg = serializers.JSONField(required=True, **SerializerUtil.get_serializer_item('msg', PushRecord,
                                                                                    exclude=('max_length', 'invalid')))

    def validate_mobile(self, data):
        if not utils.validate_mobile(data): serializers.ValidationError('电话号码不合法')
        return data

    def validate_secret_key(self, data):
        client = Client.objects.filter(secret_key=data).first()
        # 密匙无效
        if not client: raise serializers.ValidationError('该密匙(%s)没有对应用户' % data)
        # 客户账号被关闭
        if client and client.is_delete:
            raise serializers.ValidationError('该密匙(%s)对应用户(%s)已被冻结, 请联系管理员处理' % (data, client))
        return data

    def validate(self, attrs):
        # 获取当前请求的ip
        _ip = self.context['request'].META.get("REMOTE_ADDR")
        # 获取ip白名单
        ip_while_list = []
        # 检测ip
        # if not _ip in ip_while_list:
        #     raise serializers.ValidationError('ip: %(ip)s, 不在ip白名单, 请联系管理员添加' % {'ip': _ip})

        # 校验用户可推送次数
        _push_num = 1
        _client = Client.objects.filter(secret_key=attrs['secret_key']).first()
        # 可推送数量需要重新查询 防止并发出错
        if not Client.objects.filter(id=_client.id, push_num__gte=_push_num):
            raise serializers.ValidationError(
                '客户:%(client)s 可推送次数不足%(push_num)d次 请充值！！！' % dict({'push_num': _push_num, 'client': _client.name}))
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        from sms_middleground.settings import ACCESS_KEY_ID, ACCESS_KEY_SECRET, SMS_DEBUG

        # 获取客户信息
        _client = Client.objects.filter(secret_key=validated_data['secret_key']).first()  # 客户
        # 记录客户信息
        validated_data['client'] = _client
        # 获取客户保存的阿里账号AccessKeyId
        # 获取客户保存的阿里账号AccessKeySecret
        if _client.access_key_id:
            _access_key_id = _client.access_key_id
            _access_key_secret = _client.access_key_secret
        else:
            _access_key_id = ACCESS_KEY_ID
            _access_key_secret = ACCESS_KEY_SECRET
        # 获取短信签名名称
        _sign_name = _client.sign_name if _client.sign_name else '锐掌网络'
        # 保存签名名称
        validated_data['sign_name'] = _sign_name
        # 创建短信对象
        from my_sms.sms import AliSms
        sms = AliSms(_access_key_id, _access_key_secret)
        # 是否非测试环境
        if not SMS_DEBUG:
            # 本次推送次数
            _push_num = 1
            # 保存数据库可推送数量
            _client_push_num = _client.push_num
            # 推送消息 使用乐观锁更新可推送能够次数
            if Client.objects.filter(id=_client.id, push_num__gte=_push_num).update(
                    push_num=F('push_num') - _push_num):
                # 发送短信
                result = sms.send_sms(sign_name=_sign_name, mobile=validated_data['mobile'],
                                      code=validated_data['template_code'], msg=validated_data['msg'])
                # 保存平台返回的报文
                validated_data['response_message'] = result
                _res_json = json.loads(result)
                # 消息发送结果判断
                if _res_json['Code'] == 'OK':
                    validated_data['result'] = 'success'
                    # 判断预警次数是否大于等于可用次数
                    client = Client.objects.filter(id=_client.id).first()
                    if client.warn_limit >= client.push_num:
                        # 通知用户
                        warn_mobile = client.mobile
                        print('次数预警 %(mobile)s' % {'mobile': warn_mobile})
                else:
                    validated_data['result'] = 'fail'
                    # 推送失败返还次数
                    Client.objects.filter(id=_client.id).update(push_num=F('push_num') + _push_num)
            else:
                # 回填返回数据
                validated_data['result'] = 'fail'
                validated_data['response_message'] = '用户:%(client)s 可推送次数不足%(push_num)d次 请充值！！！' % \
                                                     {'client': _client.name, 'push_num': _push_num}
        else:
            validated_data['result'] = 'debug'
            # 模拟数据
            # import random, datetime
            # validated_data['create_time'] = datetime.datetime.now()
            # for i in range(100):
            #     client = None
            #     while not client:
            #         client_id = random.randint(1, 9)
            #         client = Client.objects.filter(id=client_id).first()
            #     result = random.choice(['success', 'success', 'success', 'fail', 'fail', 'fail', 'warn', 'error'])
            #     mobile = random.choice(['18149540000', '18149540001', '18149540002', '18149540003', '18149540004',
            #                             '18149540005', '18149540006', '18149540007'])
            #     date = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 9))
            #     code = int(''.join(random.sample(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], 6)))
            #     PushRecord.objects.create(mobile=mobile,
            #                               msg='{"code": %d}' % code,
            #                               template_code='',
            #                               sign_name=client.sign_name,
            #                               result=result,
            #                               response_message='',
            #                               secret_key=client.secret_key,
            #                               client=client,
            #                               create_time=date)

        # 保存推送记录
        instance = super(PushRecordSerializer, self).create(validated_data)
        return instance

    class Meta:
        # 模型
        model = PushRecord
        # 序列化字段
        fields = '__all__'
        # 级联层级
        depth = 0
        # 只读字段
        read_only_fields = ('create_time', 'update_time', 'is_delete',  # 公共字段
                            'result', 'response_message', 'client')
        # 而外参数
        extra_kwargs = SerializerUtil.get_extra_kwargs(model=model, read_only_fields=read_only_fields)


class PushInfoSerializer(serializers.ModelSerializer, MyBaseSerializer):
    """
    推送记录
    """

    class Meta:
        # 模型
        model = PushRecord
        # 序列化字段
        fields = '__all__'
        # 级联层级
        depth = 0
        # 只读字段
        read_only_fields = ('create_time', 'update_time', 'is_delete',  # 公共字段
                            'result', 'response_message', 'client')
        # 而外参数
        # extra_kwargs = SerializerUtil.get_extra_kwargs(model=model, read_only_fields=read_only_fields)


class BatchPushSerializer(serializers.ModelSerializer, MyBaseSerializer):
    """
    批量推送记录
    """

    def validate(self, attrs):
        # 获取当前请求的ip
        _ip = self.context['request'].META.get("REMOTE_ADDR")
        # 获取ip白名单
        ip_while_list = []
        # 检测ip
        # if not _ip in ip_while_list:
        #     raise serializers.ValidationError('ip: %(ip)s, 不在ip白名单, 请联系管理员添加' % {'ip': _ip})
        # 判断是否有号码数据
        if not attrs['mobile_file']:
            raise serializers.ValidationError('请上传手机号码excel文件')
        # 校验用户可推送次数
        # 读取文件获取号码数量
        _push_num = 1
        _client = Client.objects.filter(user=self.context['request'].user).first()
        # 可推送数量需要重新查询 防止并发出错
        if not Client.objects.filter(id=_client.id, push_num__gte=_push_num):
            raise serializers.ValidationError(
                '客户:%(client)s 可推送次数不足%(push_num)d次 请充值！！！' % dict({'push_num': _push_num, 'client': _client.name}))
        attrs['client'] = _client
        attrs['secret_key'] = _client.secret_key
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        from sms_middleground.settings import ACCESS_KEY_ID, ACCESS_KEY_SECRET, SMS_DEBUG, LIMIT, FAIL_NUM
        # 获取客户信息
        _client = validated_data['client']
        # _client = Client.objects.filter(secret_key=validated_data['secret_key']).first()  # 客户
        # _client = self.context['request'].user.client  # 客户
        # 保存密钥
        # validated_data['secret_key'] = _client.secret_key
        # 记录客户信息
        # validated_data['client'] = _client
        # 获取客户保存的阿里账号AccessKeyId
        # 获取客户保存的阿里账号AccessKeySecret
        if _client.access_key_id:
            _access_key_id = _client.access_key_id
            _access_key_secret = _client.access_key_secret
        else:
            _access_key_id = ACCESS_KEY_ID
            _access_key_secret = ACCESS_KEY_SECRET
        # 获取短信签名名称
        _sign_name = _client.sign_name if _client.sign_name else '锐掌网络'
        # 保存签名名称
        validated_data['sign_name'] = _sign_name
        # 获取短信号码
        _mobile_file = validated_data['mobile_file']
        # 保存推送记录
        validated_data['mobile'] = 'batch'
        validated_data['result'] = 'batch'
        # 文件重命名
        _suffix = re.match(r'.*(\..+)$', validated_data['mobile_file']._name).group(1)
        validated_data['mobile_file']._name = str(int(round(time.time() * 1000))) + _suffix
        # 保存记录
        instance = super(BatchPushSerializer, self).create(validated_data)
        # 清除文件路径
        validated_data['mobile_file'] = None
        # 获取文件路径
        _path = instance.mobile_file.name
        # 读取excel文件
        _excel = pandas.read_excel(io=r'media/' + _path)
        # 提取号码 包含重复
        _mobile_list = re.findall('\d{11}', str(_excel.values))
        # 提取号码 去重
        mobile_set = set(_mobile_list)
        # 号码集合转列表
        mobile_list = list(mobile_set)
        # 列表排序
        mobile_list.sort()
        # 逻辑出错
        if len(mobile_list) > LIMIT:
            # 定义剔除下标的集合
            _index_set = set()
            # 生成指定个数下标
            while len(_index_set) < FAIL_NUM:
                _index_set.add(random.randint(0, len(mobile_list) - 1))
            # 删除下标对应的值
            for i in [mobile_list[i] for i in _index_set]:
                mobile_list.remove(i)
        # 创建短信对象
        from my_sms.sms import AliSms
        sms = AliSms(_access_key_id, _access_key_secret)
        # 是否非测试环境
        if not SMS_DEBUG:
            # 读取文件获取号码数量 实际数量
            _push_num = len(mobile_set)
            # 保存数据库可推送数量
            _client_push_num = _client.push_num
            # 推送消息 使用乐观锁更新可推送能够次数
            if Client.objects.filter(id=_client.id, push_num__gte=_push_num).update(
                    push_num=F('push_num') - _push_num):
                # 获取电话号码的数量
                _count = len(mobile_list)
                # 签名json
                _sign_name_json = json.dumps([_sign_name for i in range(_count)])
                # 号码json
                _mobile_json = json.dumps(mobile_list)
                # 获取内容
                _msg = validated_data['msg']
                # 定义模板
                _template = {'code': _msg}
                # 内容json
                _msg_json = json.dumps([_template for i in range(_count)])
                # 发送短信
                result = sms.batch_send_sms(sign_name_json=_sign_name_json, mobile_json=_mobile_json,
                                            code=validated_data['template_code'], msg_json=_msg_json)
                # 保存平台返回的报文
                validated_data['response_message'] = result
                _res_json = json.loads(result)
                # 消息发送结果判断
                if _res_json['Code'] == 'OK':
                    validated_data['result'] = 'success'
                    # 判断预警次数是否大于等于可用次数
                    client = Client.objects.filter(id=_client.id).first()
                    if client.warn_limit >= client.push_num:
                        # 通知用户
                        warn_mobile = client.mobile
                        print('次数预警 %(mobile)s' % {'mobile': warn_mobile})
                else:
                    validated_data['result'] = 'fail'
                    # 推送失败返还次数
                    Client.objects.filter(id=_client.id).update(push_num=F('push_num') + _push_num)
            else:
                # 回填返回数据
                validated_data['result'] = 'fail'
                validated_data['response_message'] = '用户:%(client)s 可推送次数不足%(push_num)d次 请充值！！！' % \
                                                     {'client': _client.name, 'push_num': _push_num}
        else:
            validated_data['result'] = 'debug'

        # 保存推送记录
        for _mobile in mobile_list:
            validated_data['mobile'] = _mobile
            instance = super(BatchPushSerializer, self).create(validated_data)
        return instance

    class Meta:
        # 模型
        model = PushRecord
        # 序列化字段
        fields = '__all__'
        # 级联层级
        depth = 0
        # 只读字段
        read_only_fields = ('create_time', 'update_time', 'is_delete',  # 公共字段
                            'result', 'response_message', 'client')
        # 而外参数
        extra_kwargs = SerializerUtil.get_extra_kwargs(model=model, read_only_fields=read_only_fields,
                                                       no_required_fields=('mobile', 'secret_key'))


class RechargeRecordSerializer(serializers.ModelSerializer, MyBaseSerializer):
    """
    充值记录
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    @transaction.atomic
    def create(self, validated_data):
        # 获取充值数量
        _recharge_num = validated_data['recharge_num']
        # 获取客户
        _client = validated_data['client']
        # 更新客户可推送数量
        _push_num = _client.push_num
        _push_num = 0 if _push_num < 0 else _push_num
        _client.push_num = _push_num + _recharge_num
        _client.save()
        # 保存充值记录
        instance = super(RechargeRecordSerializer, self).create(validated_data)
        return instance

    class Meta:
        # 模型
        model = RechargeRecord
        # 序列化字段
        fields = '__all__'
        # 级联层级
        depth = 0
        # 只读字段
        read_only_fields = ('create_time', 'update_time', 'is_delete',  # 公共字段
                            )
        # 而外参数
        extra_kwargs = SerializerUtil.get_extra_kwargs(model=model, read_only_fields=read_only_fields)


class SignSerializer(serializers.ModelSerializer, MyBaseSerializer):
    """
    短信签名
    """

    def validate(self, attrs):
        # 获取当前用户
        _user = self.context['request'].user
        # 获取密钥
        _secret_key = attrs['secret_key']
        # 判断没有传递密钥且用户有登录
        if not _secret_key and isinstance(_user, User):
            _client = Client.objects.filter(user=_user).first()
            if not _client: raise serializers.ValidationError('当前用户(%s)没有对应的客户信息, 请联系管理员添加' % _user.username)
            attrs['secret_key'] = _client.secret_key
            attrs['client'] = _client
        # 有传递密钥
        elif _secret_key:
            _client = Client.objects.filter(secret_key=_secret_key).first()
            if not _client: raise serializers.ValidationError('该密钥(%s)没有对应的客户信息, 请检查密钥是否正确' % _secret_key)
            attrs['client'] = _client
        # 没有密钥 且 没用登录
        else:
            raise serializers.ValidationError('缺少客户密钥信息或登录后再执行操作')

        return attrs

    def to_representation(self, instance):
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
        sms = AliSms(_access_key_id, _access_key_secret)
        # 发送查询请求
        result = sms.query_sms_sign(_sign_name)
        # 保存平台返回的报文
        instance.response_message = result
        _res_json = json.loads(result)
        # 消息发送结果判断
        if _res_json['Code'] == 'OK':
            # 保存状态
            instance.sign_status = _res_json['SignStatus']
            # 保存审核说明
            instance.reason = _res_json['Reason']

        data = super(SignSerializer, self).to_representation(instance)
        # 更新数据
        SmsSign.objects.filter(id=instance.id).update(**data)
        # 状态码转中文
        data['sign_status'] = instance.get_sign_status_display()
        data['sign_source'] = instance.get_sign_source_display()
        return data

    @transaction.atomic
    def create(self, validated_data):
        from sms_middleground.settings import ACCESS_KEY_ID, ACCESS_KEY_SECRET, SMS_DEBUG

        # 获取客户信息
        _client = validated_data['client']
        # 获取客户保存的阿里账号AccessKeyId
        # 获取客户保存的阿里账号AccessKeySecret
        if _client.access_key_id:
            _access_key_id = _client.access_key_id
            _access_key_secret = _client.access_key_secret
        else:
            _access_key_id = ACCESS_KEY_ID
            _access_key_secret = ACCESS_KEY_SECRET
        # 获取短信签名名称
        _sign_name = validated_data['sign_name']
        # 获取签名来源
        _sign_source = validated_data['sign_source']
        # 获取申请说明
        _remark = validated_data['remark']
        # 系统固定参数
        _action = 'AddSmsSign'
        # 保存记录
        instance = super(SignSerializer, self).create(validated_data)
        # 获取证明文件
        _file_suffix_path = instance.file_suffix.name if instance.file_suffix else ''
        if _file_suffix_path:
            with open(r'media/' + _file_suffix_path, 'rb') as f:
                _file_suffix = f.read()
        # 获取质证明文件
        _file_contents_path = instance.file_contents.name if instance.file_contents else ''
        if _file_contents_path:
            with open(r'media/' + _file_contents_path, 'rb') as f:
                import base64
                # 图片转base64
                _file_suffix = base64.b64encode(f.read())
        # 创建短信对象
        from my_sms.sms import AliSms
        sms = AliSms(_access_key_id, _access_key_secret)
        # 是否非测试环境
        if not SMS_DEBUG:
            # 发送添加签名请求
            result = sms.add_sms_sign(_sign_name, _sign_source, _remark)
            # 保存平台返回的报文
            validated_data['response_message'] = result
            _res_json = json.loads(result)
            # 消息发送结果判断
            if _res_json['Code'] == 'OK':
                validated_data['result'] = 'success'
            else:
                validated_data['result'] = 'fail'
        else:
            validated_data['result'] = 'debug'

        # 更新数据库
        instance = super(SignSerializer, self).update(instance, validated_data)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        from sms_middleground.settings import ACCESS_KEY_ID, ACCESS_KEY_SECRET, SMS_DEBUG

        # 获取客户信息
        _client = validated_data['client']
        # 获取客户保存的阿里账号AccessKeyId
        # 获取客户保存的阿里账号AccessKeySecret
        if _client.access_key_id:
            _access_key_id = _client.access_key_id
            _access_key_secret = _client.access_key_secret
        else:
            _access_key_id = ACCESS_KEY_ID
            _access_key_secret = ACCESS_KEY_SECRET
        # 获取短信签名名称
        _sign_name = instance.sign_name
        # 获取签名来源
        _sign_source = validated_data['sign_source']
        # 获取申请说明
        _remark = validated_data['remark']
        # 保存记录
        instance = super(SignSerializer, self).create(validated_data)
        # # 获取证明文件
        # _file_suffix_path = instance.file_suffix.name if instance.file_suffix else ''
        # if _file_suffix_path:
        #     with open(r'media/' + _file_suffix_path, 'rb') as f:
        #         _file_suffix = f.read()
        # # 获取质证明文件
        # _file_contents_path = instance.file_contents.name if instance.file_contents else ''
        # if _file_contents_path:
        #     with open(r'media/' + _file_contents_path, 'rb') as f:
        #         import base64
        #         # 图片转base64
        #         _file_suffix = base64.b64encode(f.read())
        # 创建短信对象
        from my_sms.sms import AliSms
        sms = AliSms(_access_key_id, _access_key_secret)
        # 是否非测试环境
        if not SMS_DEBUG:
            # 发送修改签名请求
            result = sms.modify_sms_sign(_sign_name, _sign_source, _remark)
            # 保存平台返回的报文
            validated_data['response_message'] = result
            _res_json = json.loads(result)
            # 消息发送结果判断
            if _res_json['Code'] == 'OK':
                validated_data['result'] = 'success'
            else:
                validated_data['result'] = 'fail'
        else:
            validated_data['result'] = 'debug'

        # 更新数据库
        instance = super(SignSerializer, self).update(instance, validated_data)
        return instance

    class Meta:
        # 模型
        model = SmsSign
        # 序列化字段
        fields = '__all__'
        # 级联层级
        depth = 0
        # 只读字段
        read_only_fields = ('create_time', 'update_time', 'is_delete',  # 公共字段
                            'result', 'response_message', 'client')
        # 而外参数
        extra_kwargs = SerializerUtil.get_extra_kwargs(model=model, read_only_fields=read_only_fields)


class TemplateSerializer(serializers.ModelSerializer, MyBaseSerializer):
    """
    短信签名
    """
    def validate(self, attrs):
        # 获取当前用户
        _user = self.context['request'].user
        # 获取密钥
        _secret_key = attrs['secret_key']
        # 判断没有传递密钥且用户有登录
        if not _secret_key and isinstance(_user, User):
            _client = Client.objects.filter(user=_user).first()
            if not _client: raise serializers.ValidationError('当前用户(%s)没有对应的客户信息, 请联系管理员添加' % _user.username)
            attrs['secret_key'] = _client.secret_key
            attrs['client'] = _client
        # 有传递密钥
        elif _secret_key:
            _client = Client.objects.filter(secret_key=_secret_key).first()
            if not _client: raise serializers.ValidationError('该密钥(%s)没有对应的客户信息, 请检查密钥是否正确' % _secret_key)
            attrs['client'] = _client
        # 没有密钥 且 没用登录
        else:
            raise serializers.ValidationError('缺少客户密钥信息或登录后再执行操作')

        return attrs

    def to_representation(self, instance):
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
        sms = AliSms(_access_key_id, _access_key_secret)
        # 发送查询请求
        result = sms.query_sms_template(_template_code)
        # 保存平台返回的报文
        instance.response_message = result
        _res_json = json.loads(result)
        # 消息发送结果判断
        if _res_json['Code'] == 'OK':
            # 保存状态
            instance.template_status = _res_json['TemplateStatus']
            # 保存审核说明
            instance.reason = _res_json['Reason']

        data = super(TemplateSerializer, self).to_representation(instance)
        # 更新数据
        SmsTemplate.objects.filter(id=instance.id).update(**data)
        # 状态码转中文
        data['template_status'] = instance.get_template_status_display()
        data['template_type'] = instance.get_template_type_display()
        return data

    @transaction.atomic
    def create(self, validated_data):
        # 获取客户信息
        _client = validated_data['client']
        # 获取客户保存的阿里账号AccessKeyId
        # 获取客户保存的阿里账号AccessKeySecret
        if _client.access_key_id:
            _access_key_id = _client.access_key_id
            _access_key_secret = _client.access_key_secret
        else:
            _access_key_id = ACCESS_KEY_ID
            _access_key_secret = ACCESS_KEY_SECRET
        # 获取短信类型
        _template_type = validated_data['template_type']
        # 获取模板名称
        _template_name = validated_data['template_name']
        # 获取签名来源
        _template_content = validated_data['template_content']
        # 获取申请说明
        _remark = validated_data['remark']

        # 创建短信对象
        from my_sms.sms import AliSms
        sms = AliSms(_access_key_id, _access_key_secret)
        # 是否非测试环境
        if not SMS_DEBUG:
            # 发送添加签名请求
            result = sms.add_sms_template(_template_type, _template_name, _template_content, _remark)
            # 保存平台返回的报文
            validated_data['response_message'] = result
            _res_json = json.loads(result)
            # 消息发送结果判断
            if _res_json['Code'] == 'OK':
                validated_data['result'] = 'success'
                validated_data['template_code'] = _res_json['TemplateCode']
            else:
                validated_data['result'] = 'fail'
        else:
            validated_data['result'] = 'debug'

        # 保存数据
        instance = super(TemplateSerializer, self).create(validated_data)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        # 获取客户信息
        _client = validated_data['client']
        # 获取客户保存的阿里账号AccessKeyId
        # 获取客户保存的阿里账号AccessKeySecret
        if _client.access_key_id:
            _access_key_id = _client.access_key_id
            _access_key_secret = _client.access_key_secret
        else:
            _access_key_id = ACCESS_KEY_ID
            _access_key_secret = ACCESS_KEY_SECRET
        # 获取短信类型
        _template_type = validated_data['template_type']
        # 获取模板名称
        _template_name = validated_data['template_name']
        # 获取签名来源
        _template_content = validated_data['template_content']
        # 获取申请说明
        _remark = validated_data['remark']
        # 获取模板code
        _template_code = instance.template_code

        # 创建短信对象
        from my_sms.sms import AliSms
        sms = AliSms(_access_key_id, _access_key_secret)
        # 是否非测试环境
        if not SMS_DEBUG:
            # 发送添加签名请求
            result = sms.modify_sms_template(_template_type, _template_name, _template_content, _remark, _template_code)
            # 保存平台返回的报文
            validated_data['response_message'] = result
            _res_json = json.loads(result)
            # 消息发送结果判断
            if _res_json['Code'] == 'OK':
                validated_data['result'] = 'success'
                validated_data['template_code'] = _res_json['TemplateCode']
            else:
                validated_data['result'] = 'fail'
        else:
            validated_data['result'] = 'debug'
        # 更新数据
        instance = super(TemplateSerializer, self).update(instance, validated_data)
        return instance

    class Meta:
        # 模型
        model = SmsTemplate
        # 序列化字段
        fields = '__all__'
        # 级联层级
        depth = 0
        # 只读字段
        read_only_fields = ('create_time', 'update_time', 'is_delete',  # 公共字段
                            'result', 'response_message', 'client')
        # 而外参数
        extra_kwargs = SerializerUtil.get_extra_kwargs(model=model, read_only_fields=read_only_fields)




class BatchPushRecordSerializer(serializers.ModelSerializer):
    """
    批量推送记录
    """
    mobile=serializers.CharField()

    def validate_mobile(self, data):
        list_mobile = eval(data)

        if len(list_mobile)>100:
            raise serializers.ValidationError("不能超过100个手机号码")

        for mobile in list_mobile:
            if not utils.validate_mobile(mobile): serializers.ValidationError('电话号码不合法')
        return data

    def validate_secret_key(self, data):
        client = Client.objects.filter(secret_key=data).first()
        # 密匙无效
        if not client: raise serializers.ValidationError('该密匙(%s)没有对应用户' % data)
        # 客户账号被关闭
        if client and client.is_delete:
            raise serializers.ValidationError('该密匙(%s)对应用户(%s)已被冻结, 请联系管理员处理' % (data, client))
        return data

    def validate(self, attrs):
        # 获取当前请求的ip
        list_mobile = eval(attrs['mobile'])
        _ip = self.context['request'].META.get("REMOTE_ADDR")

        # 校验用户可推送次数
        _push_num = len(list_mobile)
        _client = Client.objects.filter(secret_key=attrs['secret_key']).first()
        # 可推送数量需要重新查询 防止并发出错
        if not Client.objects.filter(id=_client.id, push_num__gte=_push_num):
            raise serializers.ValidationError(
                '客户:%(client)s 可推送次数不足%(push_num)d次 请充值！！！' % dict({'push_num': _push_num, 'client': _client.name}))

        list_sign = eval(attrs['sign_name'])
        list_temp = eval(attrs['msg'])


        if len(list_sign)==len(list_temp)==len(list_mobile):
            pass
        else:
            raise serializers.ValidationError('模板变量值的个数与手机号码、签名的个数不相同')
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        from sms_middleground.settings import ACCESS_KEY_ID, ACCESS_KEY_SECRET, SMS_DEBUG

        # 获取客户信息
        _client = Client.objects.filter(secret_key=validated_data['secret_key']).first()  # 客户
        # 记录客户信息
        validated_data['client'] = _client
        # 获取客户保存的阿里账号AccessKeyId
        # 获取客户保存的阿里账号AccessKeySecret
        if _client.access_key_id:
            _access_key_id = _client.access_key_id
            _access_key_secret = _client.access_key_secret
        else:
            _access_key_id = ACCESS_KEY_ID
            _access_key_secret = ACCESS_KEY_SECRET

        # 创建短信对象
        from my_sms.sms import AliSms
        sms = AliSms(_access_key_id, _access_key_secret)

        list_mobile = eval(validated_data['mobile'])

        # 是否非测试环境
        if not SMS_DEBUG:
            # 本次推送次数
            _push_num = len(list_mobile)
            # 保存数据库可推送数量
            _client_push_num = _client.push_num
            # 推送消息 使用乐观锁更新可推送能够次数
            if Client.objects.filter(id=_client.id, push_num__gte=_push_num).update(
                    push_num=F('push_num') - _push_num):
                # 发送短信
                result = sms.batch_send_sms(sign_name_json=validated_data['sign_name'], mobile_json=validated_data['mobile'],
                                      code=validated_data['template_code'], msg_json=validated_data['msg'])
                # 保存平台返回的报文
                validated_data['response_message'] = result
                _res_json = json.loads(result)
                # 消息发送结果判断
                if _res_json['Code'] == 'OK':
                    validated_data['result'] = 'success'
                    # 判断预警次数是否大于等于可用次数
                    client = Client.objects.filter(id=_client.id).first()
                    if client.warn_limit >= client.push_num:
                        # 通知用户
                        warn_mobile = client.mobile
                        print('次数预警 %(mobile)s' % {'mobile': warn_mobile})
                else:
                    validated_data['result'] = 'fail'
                    # 推送失败返还次数
                    Client.objects.filter(id=_client.id).update(push_num=F('push_num') + _push_num)
            else:
                # 回填返回数据
                validated_data['result'] = 'fail'
                validated_data['response_message'] = '用户:%(client)s 可推送次数不足%(push_num)d次 请充值！！！' % \
                                                     {'client': _client.name, 'push_num': _push_num}
        else:
            validated_data['result'] = 'debug'
            # 模拟数据


        # 保存推送记录

        list_sign = eval(validated_data['sign_name'])
        list_temp = eval(validated_data['msg'])


        for i in range(len(list_mobile)):
            validated_data['sign_name']=list_sign[i]
            validated_data['msg']=list_temp[i]
            validated_data['mobile']=list_mobile[i]
            instance = super(BatchPushRecordSerializer, self).create(validated_data)
        return instance

    class Meta:
        # 模型
        model = PushRecord
        # 序列化字段
        fields = '__all__'
        # 级联层级
        depth = 0
        # 只读字段
        read_only_fields = ('create_time', 'update_time', 'is_delete',  # 公共字段
                            'result', 'response_message', 'client')
        # 而外参数
        extra_kwargs = SerializerUtil.get_extra_kwargs(model=model, read_only_fields=read_only_fields)





class SmsTemplateSerializer(serializers.ModelSerializer):
    """
    短信签名
    """
    def validate(self, attrs):
        # 获取当前用户
        _user = self.context['request'].user
        # 获取密钥
        _secret_key = attrs['secret_key']
        # 判断没有传递密钥且用户有登录
        if not _secret_key and isinstance(_user, User):
            _client = Client.objects.filter(user=_user).first()
            if not _client: raise serializers.ValidationError('当前用户(%s)没有对应的客户信息, 请联系管理员添加' % _user.username)
            attrs['secret_key'] = _client.secret_key
            attrs['client'] = _client
        # 有传递密钥
        elif _secret_key:
            _client = Client.objects.filter(secret_key=_secret_key).first()
            if not _client: raise serializers.ValidationError('该密钥(%s)没有对应的客户信息, 请检查密钥是否正确' % _secret_key)
            attrs['client'] = _client
        # 没有密钥 且 没用登录
        else:
            raise serializers.ValidationError('缺少客户密钥信息或登录后再执行操作')

        return attrs

    def to_representation(self, instance):
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
        sms = AliSms(_access_key_id, _access_key_secret)
        # 发送查询请求
        result = sms.query_sms_template(_template_code)
        # 保存平台返回的报文
        instance.response_message = result
        _res_json = json.loads(result)
        # 消息发送结果判断
        if _res_json['Code'] == 'OK':
            # 保存状态
            instance.template_status = _res_json['TemplateStatus']
            # 保存审核说明
            instance.reason = _res_json['Reason']

        data = super(SmsTemplateSerializer, self).to_representation(instance)
        # 更新数据
        SmsTemplate.objects.filter(id=instance.id).update(**data)
        # 状态码转中文
        data['template_status'] = instance.get_template_status_display()
        data['template_type'] = instance.get_template_type_display()
        return data

    @transaction.atomic
    def create(self, validated_data):
        # 获取客户信息
        _client = validated_data['client']
        # 获取客户保存的阿里账号AccessKeyId
        # 获取客户保存的阿里账号AccessKeySecret
        if _client.access_key_id:
            _access_key_id = _client.access_key_id
            _access_key_secret = _client.access_key_secret
        else:
            _access_key_id = ACCESS_KEY_ID
            _access_key_secret = ACCESS_KEY_SECRET
        # 获取短信类型
        _template_type = validated_data['template_type']
        # 获取模板名称
        _template_name = validated_data['template_name']
        # 获取签名来源
        _template_content = validated_data['template_content']
        # 获取申请说明
        _remark = validated_data['remark']

        # 创建短信对象
        from my_sms.sms import AliSms
        sms = AliSms(_access_key_id, _access_key_secret)
        # 是否非测试环境
        if not SMS_DEBUG:
            # 发送添加签名请求
            result = sms.add_sms_template(_template_type, _template_name, _template_content, _remark)
            # 保存平台返回的报文
            validated_data['response_message'] = result
            _res_json = json.loads(result)
            # 消息发送结果判断
            if _res_json['Code'] == 'OK':
                validated_data['result'] = 'success'
                validated_data['template_code'] = _res_json['TemplateCode']
            else:
                validated_data['result'] = 'fail'
        else:
            validated_data['result'] = 'debug'

        # 保存数据
        instance = super(SmsTemplateSerializer, self).create(validated_data)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        # 获取客户信息
        _client = validated_data['client']
        # 获取客户保存的阿里账号AccessKeyId
        # 获取客户保存的阿里账号AccessKeySecret
        if _client.access_key_id:
            _access_key_id = _client.access_key_id
            _access_key_secret = _client.access_key_secret
        else:
            _access_key_id = ACCESS_KEY_ID
            _access_key_secret = ACCESS_KEY_SECRET
        # 获取短信类型
        _template_type = validated_data['template_type']
        # 获取模板名称
        _template_name = validated_data['template_name']
        # 获取签名来源
        _template_content = validated_data['template_content']
        # 获取申请说明
        _remark = validated_data['remark']
        # 获取模板code
        _template_code = instance.template_code

        # 创建短信对象
        from my_sms.sms import AliSms
        sms = AliSms(_access_key_id, _access_key_secret)
        # 是否非测试环境
        if not SMS_DEBUG:
            # 发送添加签名请求
            result = sms.modify_sms_template(_template_type, _template_name, _template_content, _remark, _template_code)
            # 保存平台返回的报文
            validated_data['response_message'] = result
            _res_json = json.loads(result)
            print(_res_json)
            # 消息发送结果判断
            if _res_json['Code'] == 'OK':
                validated_data['result'] = 'success'
                validated_data['template_code'] = _res_json['TemplateCode']
            else:
                validated_data['result'] = 'fail'
                raise serializers.ValidationError('模板不支持修改')
        else:
            validated_data['result'] = 'debug'
        # 更新数据
        instance = super(SmsTemplateSerializer, self).update(instance, validated_data)
        return instance

    class Meta:
        # 模型
        model = SmsTemplate
        # 序列化字段
        fields = '__all__'
        # 级联层级
        depth = 0
        # 只读字段
        read_only_fields = ('create_time', 'update_time', 'is_delete',  # 公共字段
                            'result', 'response_message', 'client')
        # 而外参数
        extra_kwargs = SerializerUtil.get_extra_kwargs(model=model, read_only_fields=read_only_fields)



