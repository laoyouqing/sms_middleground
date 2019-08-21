# coding=utf-8
import re, json, datetime, time
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.db import transaction
from django.db.models import F

from my_base.base_serializers import MyBaseSerializer, SerializerUtil
from my_utils import utils
from apps.report.models import Report
from apps.record.models import PushRecord


class ReportSerializer(serializers.ModelSerializer, MyBaseSerializer):
    """
    统计
    """
    def to_representation(self, instance):
        data = super(ReportSerializer, self).to_representation(instance)
        # 获取json文件名称
        _json_name = re.sub(r'-', '', data['date'])
        # 读取json文件
        with open('report_json/%s.json' % _json_name, 'r', encoding='utf-8') as f:
            data['chart_json'] = f.read()
        return data

    @transaction.atomic()
    def create(self, validated_data):
        # 定义统计字典
        report_dict = {}
        # 定义实例
        instance = None
        # 获取所有推送记录
        _push_list = PushRecord.objects.all()
        # 遍历推送记录
        for _push in _push_list:
            # 初始化dict
            _push_dict = {}
            _user_push_dict = {}
            # 模板
            _template_dict = {
                'success': 0,  # 成功
                'fail': 0,  # 失败
                'error': 0,  # 错误
                'debug': 0,  # 调试
                'warn': 0,  # 预警
                'total': 0,  # 当日总数(成功+失败)
                'real_total': 0,  # 当日总数+调试+错误+预警
                'success_rate': 0.0000,  # 当日成功率(成功/总数)
                'real_success_rate': 0.0000,  # 当日实际成功率((成功+调试+预警)/实际总数)
                'fail_rate': 0.0000,  # 当日失败率(失败/总数)
                'real_fail_rate': 0.0000,  # 当日实际失败率((失败+错误)/实际总数)
            }
            # 推送结果
            _result = _push.result if _push.result else 'debug'
            # 返回报文
            _response_message = _push.response_message
            # 客户
            _client = _push.client
            # 客户名称
            _name = _client.name if _client else '测试'
            # 创建时间
            _create_time = _push.create_time
            # 创建日期
            _create_date = _create_time.strftime('%Y-%m-%d')
            # 判断统计字典中是否有当前记录的创建日期
            if _create_date not in report_dict.keys():
                # 创建当前日期
                report_dict[_create_date] = {}
            # 判断统计字典中是否有当前记录的总数
            if 'total' in report_dict.get(_create_date).keys():
                # 获取
                _push_dict = report_dict[_create_date]['total']
            else:
                # 创建
                _push_dict = _template_dict
            # 判断统计字典中是否有当前记录的用户
            if _name in report_dict.get(_create_date).keys():
                # 获取用户数据
                _user_push_dict = report_dict[_create_date][_name]
            else:
                # 创建用户数据
                _user_push_dict = _template_dict
            # 统计对应结果的数量
            _push_dict[_result] += 1
            _user_push_dict[_result] += 1  # 用户
            # 回填统计结果
            report_dict[_create_date]['total'] = _push_dict
            report_dict[_create_date][_name] = _user_push_dict  # 用户
        # 遍历统计字典计算成功失败率及总数
        for (_date, _save_dict) in report_dict.items():
            for (_key, _value) in report_dict.get(_date).items():
                # 计算总数
                report_dict[_date][_key]['total'] = _value['success'] + _value['fail']
                # 实际总数
                report_dict[_date][_key]['real_total'] = report_dict[_date][_key]['total'] + \
                                                  _value['error'] + _value['debug'] + _value['warn']
                # 判断总数是否合法
                if report_dict[_date][_key]['total'] > 0:
                    # 成功率
                    report_dict[_date][_key]['success_rate'] = _value['success'] / report_dict[_date][_key]['total']
                    report_dict[_date][_key]['success_rate'] = round(report_dict[_date][_key]['success_rate'], 4)

                    # 失败率
                    report_dict[_date][_key]['fail_rate'] = _value['fail'] / report_dict[_date][_key]['total']
                    report_dict[_date][_key]['fail_rate'] = round(report_dict[_date][_key]['fail_rate'], 4)
                # 判断实际总数是否合法
                if report_dict[_date][_key]['real_total'] > 0:
                    # 实际成功率
                    report_dict[_date][_key]['real_success_rate'] = (_value['success'] + _value['debug'] + _value['warn']) / \
                                                             report_dict[_date][_key]['real_total']
                    report_dict[_date][_key]['real_success_rate'] = round(report_dict[_date][_key]['real_success_rate'], 4)
                    # 实际失败率
                    report_dict[_date][_key]['real_fail_rate'] = (_value['fail'] + _value['error']) / \
                                                             report_dict[_date][_key]['real_total']
                    report_dict[_date][_key]['real_fail_rate'] = round(report_dict[_date][_key]['real_fail_rate'], 4)
                # 数据库字段只存储总数
                if _key == 'total':
                    # 将数据存入数据库
                    report_obj = Report.objects.filter(date=_date).first()
                    # 赋值
                    _validated_data = _value
                    _validated_data['chart_json'] = re.sub(r'\'', '"', str(_save_dict))
                    _validated_data['chart_json'] = re.sub(r'[\t\n\r\f\v\s]+', '', _validated_data['chart_json'])
                    # print(_validated_data['chart_json'], len(_validated_data['chart_json']))
                    # 将json保存到json文件
                    with open('report_json/%s.json' % re.sub(r'-', '', _date), 'w', encoding='utf-8') as f:
                        f.write(_validated_data['chart_json'])
                    # json 字符串过长不保存到数据库
                    _validated_data['chart_json'] = ''
                    _validated_data['date'] = _date
                    if report_obj:  # 记录存在 修改
                        instance = super(ReportSerializer, self).update(report_obj, _validated_data)
                    else:  # 记录不存在 新增
                        instance = super(ReportSerializer, self).create(_validated_data)

        return instance

    class Meta:
        # 模型
        model = Report
        # 序列化字段
        fields = '__all__'
        # 级联层级
        depth = 0
        # 只读字段
        # read_only_fields = ('create_time', 'update_time', 'is_delete',  # 公共字段
        #                     )
        read_only_fields = tuple(utils.get_model_fields(model, exclude_list=[]))
        # 而外参数
        extra_kwargs = SerializerUtil.get_extra_kwargs(model=model, read_only_fields=read_only_fields)
