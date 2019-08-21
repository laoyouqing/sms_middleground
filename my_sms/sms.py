# !/usr/bin/env python
# coding=utf-8
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class AliSms(object):
    """
    阿里云短信服务
    """
    def __init__(self, access_key_id, access_key_secret=None):
        """
        初始化短信对象
        :param access_key_id: 阿里云账号AccessKeyId
        :param access_key_secret: 阿里云账号AccessKeySecret
        """
        self.client = AcsClient(access_key_id, access_key_secret, 'default')
        self.request = CommonRequest()
        self.request.set_accept_format('json')
        self.request.set_domain('dysmsapi.aliyuncs.com')
        self.request.set_method('POST')
        self.request.set_protocol_type('https')  # https | http
        self.request.set_version('2017-05-25')

    def send_sms(self, sign_name, mobile, code, msg):
        """
        发送单条短信
        :param sign_name: 短信签名名称
        :param mobile: 号码
        :param code: 短信模板id
        :param msg: 短信内容 json
        :return:
        """
        # 添加接口类型
        self.request.set_action_name('SendSms')
        # 添加号码
        self.request.add_query_param('PhoneNumbers', mobile)
        # 添加签名名称
        self.request.add_query_param('SignName', sign_name)
        # 添加模板id
        self.request.add_query_param('TemplateCode', code)
        # 添加短信内容
        self.request.add_query_param('TemplateParam', msg)

        response = self.client.do_action_with_exception(self.request)

        return str(response, encoding='utf-8')

    def batch_send_sms(self, sign_name_json, mobile_json, code, msg_json):
        """
        发送批量短信
        :param sign_name_json: 短信签名名称json数组
        :param mobile_json: 号码json数组
        :param code: 短信模板id
        :param msg_json: 短信内容json数组
        :return:
        """
        # 添加接口类型
        self.request.set_action_name('SendBatchSms')
        # 添加号码
        self.request.add_query_param('PhoneNumberJson', mobile_json)
        # 添加签名名称
        self.request.add_query_param('SignNameJson', sign_name_json)
        # 添加模板id
        self.request.add_query_param('TemplateCode', code)
        # 添加短信内容
        self.request.add_query_param('TemplateParamJson', msg_json)

        response = self.client.do_action_with_exception(self.request)

        return str(response, encoding='utf-8')

    def add_sms_sign(self, sign_name, sign_source, remark, action='AddSmsSign', suffix=None, content=None):
        """
        发送批量短信
        :param sign_name 签名名称
        :param sign_source 签名来源
        :param remark 申请说明
        :param action 接口类型
        :param suffix 签名证明
        :param content 签名质证明文件
        :return:
        """
        # 添加接口类型
        self.request.set_action_name(action)
        # 添加签名名称
        self.request.add_query_param('SignName', sign_name)
        # 添加签名来源
        self.request.add_query_param('SignSource', sign_source)
        # 添加申请说明
        self.request.add_query_param('Remark', remark)
        # 添加签名证明
        if suffix:
            self.request.add_query_param('SignFileList.N.FileSuffix', 'http://image.baidu.com/search/detail?ct=503316480&z=0&ipn=false&word=%E5%9B%BE%E7%89%87%20%E5%A4%B4%E5%83%8F&hs=0&pn=0&spn=0&di=58300&pi=0&rn=1&tn=baiduimagedetail&is=0%2C0&ie=utf-8&oe=utf-8&cl=2&lm=-1&cs=2474103507%2C1473790158&os=1884600632%2C1381218248&simid=0%2C0&adpicid=0&lpn=0&ln=30&fr=ala&fm=&sme=&cg=head&bdtype=0&oriquery=%E5%9B%BE%E7%89%87%20%E5%A4%B4%E5%83%8F&objurl=http%3A%2F%2Fimg5.duitang.com%2Fuploads%2Fitem%2F201410%2F11%2F20141011040700_3iXsj.thumb.700_0.jpeg&fromurl=ippr_z2C%24qAzdH3FAzdH3Fooo_z%26e3B17tpwg2_z%26e3Bv54AzdH3Frj5rsjAzdH3F4ks52AzdH3Fdd89890anAzdH3F1jpwtsAzdH3F&gsm=0&islist=&querylist=')
        # 添加签名质证明文件
        if content:
            self.request.add_query_param('SignFileList.N.FileContents', 'http://image.baidu.com/search/detail?ct=503316480&z=0&ipn=false&word=%E5%9B%BE%E7%89%87%20%E5%A4%B4%E5%83%8F&hs=0&pn=0&spn=0&di=58300&pi=0&rn=1&tn=baiduimagedetail&is=0%2C0&ie=utf-8&oe=utf-8&cl=2&lm=-1&cs=2474103507%2C1473790158&os=1884600632%2C1381218248&simid=0%2C0&adpicid=0&lpn=0&ln=30&fr=ala&fm=&sme=&cg=head&bdtype=0&oriquery=%E5%9B%BE%E7%89%87%20%E5%A4%B4%E5%83%8F&objurl=http%3A%2F%2Fimg5.duitang.com%2Fuploads%2Fitem%2F201410%2F11%2F20141011040700_3iXsj.thumb.700_0.jpeg&fromurl=ippr_z2C%24qAzdH3FAzdH3Fooo_z%26e3B17tpwg2_z%26e3Bv54AzdH3Frj5rsjAzdH3F4ks52AzdH3Fdd89890anAzdH3F1jpwtsAzdH3F&gsm=0&islist=&querylist=')

        response = self.client.do_action_with_exception(self.request)

        return str(response, encoding='utf-8')

    def delete_sms_sign(self, sign_name, action='DeleteSmsSign'):
        """
        删除短信签名
        :param sign_name 短信签名
        :return:
        """
        # 添加接口类型
        self.request.set_action_name(action)
        # 添加模板code
        self.request.add_query_param('SignName', sign_name)

        response = self.client.do_action_with_exception(self.request)

        return str(response, encoding='utf-8')

    def modify_sms_sign(self, sign_name, sign_source, remark, action='ModifySmsSign', suffix=None, content=None):
        """
        发送批量短信
        :param sign_name 签名名称
        :param sign_source 签名来源
        :param remark 申请说明
        :param action 接口类型
        :param suffix 签名证明
        :param content 签名质证明文件
        :return:
        """
        # 添加接口类型
        self.request.set_action_name(action)
        # 添加签名名称
        self.request.add_query_param('SignName', sign_name)
        # 添加签名来源
        self.request.add_query_param('SignSource', sign_source)
        # 添加申请说明
        self.request.add_query_param('Remark', remark)
        # 添加签名证明
        if suffix:
            self.request.add_query_param('SignFileList.N.FileSuffix', 'http://image.baidu.com/search/detail?ct=503316480&z=0&ipn=false&word=%E5%9B%BE%E7%89%87%20%E5%A4%B4%E5%83%8F&hs=0&pn=0&spn=0&di=58300&pi=0&rn=1&tn=baiduimagedetail&is=0%2C0&ie=utf-8&oe=utf-8&cl=2&lm=-1&cs=2474103507%2C1473790158&os=1884600632%2C1381218248&simid=0%2C0&adpicid=0&lpn=0&ln=30&fr=ala&fm=&sme=&cg=head&bdtype=0&oriquery=%E5%9B%BE%E7%89%87%20%E5%A4%B4%E5%83%8F&objurl=http%3A%2F%2Fimg5.duitang.com%2Fuploads%2Fitem%2F201410%2F11%2F20141011040700_3iXsj.thumb.700_0.jpeg&fromurl=ippr_z2C%24qAzdH3FAzdH3Fooo_z%26e3B17tpwg2_z%26e3Bv54AzdH3Frj5rsjAzdH3F4ks52AzdH3Fdd89890anAzdH3F1jpwtsAzdH3F&gsm=0&islist=&querylist=')
        # 添加签名质证明文件
        if content:
            self.request.add_query_param('SignFileList.N.FileContents', 'http://image.baidu.com/search/detail?ct=503316480&z=0&ipn=false&word=%E5%9B%BE%E7%89%87%20%E5%A4%B4%E5%83%8F&hs=0&pn=0&spn=0&di=58300&pi=0&rn=1&tn=baiduimagedetail&is=0%2C0&ie=utf-8&oe=utf-8&cl=2&lm=-1&cs=2474103507%2C1473790158&os=1884600632%2C1381218248&simid=0%2C0&adpicid=0&lpn=0&ln=30&fr=ala&fm=&sme=&cg=head&bdtype=0&oriquery=%E5%9B%BE%E7%89%87%20%E5%A4%B4%E5%83%8F&objurl=http%3A%2F%2Fimg5.duitang.com%2Fuploads%2Fitem%2F201410%2F11%2F20141011040700_3iXsj.thumb.700_0.jpeg&fromurl=ippr_z2C%24qAzdH3FAzdH3Fooo_z%26e3B17tpwg2_z%26e3Bv54AzdH3Frj5rsjAzdH3F4ks52AzdH3Fdd89890anAzdH3F1jpwtsAzdH3F&gsm=0&islist=&querylist=')

        response = self.client.do_action_with_exception(self.request)

        return str(response, encoding='utf-8')

    def query_sms_sign(self, sign_name, action='QuerySmsSign'):
        """
        查询短信签名
        :param sign_name 签名名称
        :return:
        """
        # 添加接口类型
        self.request.set_action_name(action)
        # 添加签名名称
        self.request.add_query_param('SignName', sign_name)

        response = self.client.do_action_with_exception(self.request)

        return str(response, encoding='utf-8')

    def add_sms_template(self, template_type, template_name, template_content, remark, action='AddSmsTemplate'):
        """
        新增短信模板
        :param template_type 短信类型
        :param template_name 模板名称
        :param template_content 模板内容
        :param remark 申请说明
        :param action 接口类型
        :return:
        """
        # 添加接口类型
        self.request.set_action_name(action)
        # 添加签名名称
        self.request.add_query_param('TemplateType', template_type)
        # 添加签名名称
        self.request.add_query_param('TemplateName', template_name)
        # 添加签名来源
        self.request.add_query_param('TemplateContent', template_content)
        # 添加申请说明
        self.request.add_query_param('Remark', remark)

        response = self.client.do_action_with_exception(self.request)

        return str(response, encoding='utf-8')

    def delete_sms_template(self, template_code, action='DeleteSmsTemplate'):
        """
        删除短信模板
        :param template_code 短信类型
        :return:
        """
        # 添加接口类型
        self.request.set_action_name(action)
        # 添加模板code
        self.request.add_query_param('TemplateCode', template_code)

        response = self.client.do_action_with_exception(self.request)

        return str(response, encoding='utf-8')

    def modify_sms_template(self, template_type, template_name, template_content, remark, template_code, action='ModifySmsTemplate'):
        """
        修改短信模板
        :param template_type 短信类型
        :param template_name 模板名称
        :param template_content 模板内容
        :param remark 申请说明
        :param template_code 模板code
        :param action 接口类型
        :return:
        """
        # 添加接口类型
        self.request.set_action_name(action)
        # 添加签名名称
        self.request.add_query_param('TemplateType', template_type)
        # 添加签名名称
        self.request.add_query_param('TemplateName', template_name)
        # 添加签名来源
        self.request.add_query_param('TemplateContent', template_content)
        # 添加申请说明
        self.request.add_query_param('Remark', remark)
        # 添加模板code
        self.request.add_query_param('TemplateCode', template_code)

        response = self.client.do_action_with_exception(self.request)

        return str(response, encoding='utf-8')

    def query_sms_template(self, template_code, action='QuerySmsTemplate'):
        """
        查询短信模板
        :param template_code 短信类型
        :return:
        """
        # 添加接口类型
        self.request.set_action_name(action)
        # 添加模板code
        self.request.add_query_param('TemplateCode', template_code)

        response = self.client.do_action_with_exception(self.request)

        return str(response, encoding='utf-8')
