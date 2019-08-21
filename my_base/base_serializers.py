import os, json, re, copy
from rest_framework import serializers
from django.db import transaction
from my_utils import utils
from my_base.base_model import BaseModel
from my_utils.auto_utils import auto_create_model_fields_2_file
from apps.record.models import R_C_LIST
# from apps.param.models import P_C_LIST
from apps.user.models import U_C_LIST
from apps.report.models import REPORT_C_LIST


class SerializerUtil(object):
    MATCH_EXP_ONE = r'^(\w+;)+$'  # 匹配普通间隔
    MATCH_EXP_TWO = r'^(\w+\|\w+;)+$'  # 匹配key-value间隔
    MESSAGE_ONE = '格式不正确，例：1;2;'  # 一类提示信息
    MESSAGE_TWO = '格式不正确，例：a|1;b|2;'  # 二类提示信息
    FINDALL_EXP_ONE = r'(\w+);'  # 搜索普通间隔
    FINDALL_EXP_TWO = r'(\w+)\|\w+;'  # 搜索key-value间隔
    FINDALL_EXP_VALUE = r'(\w+)\|(\w+);'  # 搜索key-value间隔

    CLASS_LIST = R_C_LIST + U_C_LIST + REPORT_C_LIST

    default_error_messages = {
        'blank': '%(label)s, 不能为空',
        'invalid': '%(label)s, 数据无效',
        'null': '%(label)s, 不能为空',
        'required': '%(label)s, 为必填',
        "max_length": "%(label)s,最大长度为, %(max_length)d",
        "min_length": "%(label)s,长度不能小于, %(min_length)d",
    }

    @classmethod
    def get_error_messages(cls, name='', max_length=30, min_length=0, exclude=()):
        """
        生成默认的校验错误信息提示
        :param name: 字段名称
        :param max_length: 字符串最大长度
        :param min_length: 字符串最小长度
        :return: 字典
        """
        dict = {}
        for (key, value) in cls.default_error_messages.items():
            # 剔除响应提示
            if key in exclude:
                continue
            else:
                dict[key] = value % {'label': name, 'max_length': max_length, 'min_length': min_length}

        return dict

    @staticmethod
    def param_format_validate(data, match_exp=MATCH_EXP_TWO, message=MESSAGE_TWO):
        """
        自定义判断格式方法
        :param data: 检验参数
        :param match_exp: 正则表达式
        :param message: 错误信息
        :return: True | False
        """
        new_data = data
        if data:
            new_data = re.sub(r'；', ';', data)
        else:
            return new_data
        exp_data = re.match(match_exp, new_data)
        if not exp_data: raise serializers.ValidationError(message)

        return new_data

    @staticmethod
    def param_validate(obj, key, data, findall_exp=FINDALL_EXP_TWO):
        """
        校验数据是否来自系统参数配置
        :param obj: 参数模型对象
        :param key: 参数字段名称
        :param data: 校验数据
        :param findall_exp: 正则表达式
        :return: 校验结果 True | False
        """
        param = obj.objects.all().first()
        if not param: raise serializers.ValidationError('请联系管理员配置系统参数')

        value = getattr(param, key)
        if not value: return True
        value_list = re.findall(findall_exp, value)

        if not re.match(r'^\w+$', data) or data not in value_list:
            raise serializers.ValidationError('参数错误，参数值应从(' + re.sub(r'[;；]', ', ', value) + ')中选择')
            # raise serializers.ValidationError('参数错误，参数值应从(' + ', '.join(value_list) + ')中选择')

    @staticmethod
    def value_validate(obj, key, data, message, list_str=True, exp_sep=r'[；;]'):
        """
        校验数据的正确性
        :param obj: 校验对象
        :param key: 对象的键
        :param data: 校验的数据
        :param message: 返回提示
        :param list_str: 是否可以分割
        :param exp_sep: 分隔符
        :return:
        """
        if list_str:
            for val in utils.list_str_2_list(data, exp_sep=exp_sep):
                dict = {
                    key: val
                }
                if not obj.objects.filter(**dict).first(): raise serializers.ValidationError(message)

    @staticmethod
    def param_list_validate(obj, key, data):
        """
        校验数据是否来自数据库
        :param obj: 参数模型对象
        :param key: 参数字段名称
        :param data: 校验数据
        :return: 校验结果 True | False
        """
        param_list = obj.objects.all()
        value_list = [str(getattr(param, key)) for param in param_list]
        if data not in value_list: raise serializers.ValidationError('参数错误，参数值应从(' + ', '.join(value_list) + ')中选择')

    @staticmethod
    def get_param_dict(obj, key, findall_exp=FINDALL_EXP_VALUE):
        """
        返回系统参数数据的字典
        :param obj: 参数模型类
        :param key: 字段名称
        :param data: 参数应为名称
        :param findall_exp: 正则表达式
        :return: 参数数据的字典
        """
        param = obj.objects.all().first()
        if not param: return None
        value = getattr(param, key)
        value_list = re.findall(findall_exp, value)
        return {k: v for (k, v) in value_list}

    @staticmethod
    def get_param_value(obj, key, data, findall_exp=FINDALL_EXP_VALUE):
        """
        返回系统参数数据对应的中文名称
        :param obj: 参数模型类
        :param key: 字段名称
        :param data: 参数应为名称
        :param findall_exp: 正则表达式
        :return: 参数数据对应的中文名称
        """
        dict = __class__.get_param_dict(obj, key, findall_exp)
        if dict:
            return dict.get(data)
        return '错误'

    @staticmethod
    def get_param_value_list_str(obj, key, data_list, findall_exp=FINDALL_EXP_VALUE):
        """
        返回系统参数数据对应的中文名称列表字符串
        :param obj: 参数模型类
        :param key: 字段名称
        :param data_list: 参数应为名称列表
        :param findall_exp: 正则表达式
        :return: 参数数据对应的中文名称
        """
        dict = __class__.get_param_dict(obj, key, findall_exp)
        if dict:
            ret_list = []
            for data in data_list:
                ret_list.append(dict.get(data))
            return ';'.join(ret_list) + ';'
        return '错误'

    @staticmethod
    def add_param_value_to_instance(obj, key_list, param_key_list, instance, many=[]):
        """
        为返回值添加英文数据中文解释
        :param obj: 参数模型类
        :param key_list: 需添加的字段名称列表
        :param param_key_list: 字段名称列表
        :param instance: 返回数据字典
        :param many: 多值的字符串列表
        :return: 返回数据字典
        """
        for i, param_key in enumerate(param_key_list):
            if key_list[i] in many:
                instance[key_list[i] + '_name'] = __class__.get_param_value_list_str(obj=obj, key=param_key,
                                                                                     data_list=utils.list_str_2_list(
                                                                                         instance[key_list[i]]))
            else:
                instance[key_list[i] + '_name'] = __class__.get_param_value(obj=obj, key=param_key,
                                                                            data=instance[key_list[i]])
        return instance

    @staticmethod
    def add_value_name_to_instance(obj, key_list, value_key_list, instance, show_key='name', many=[]):
        """
        为返回值添加英文数据中文解释
        :param obj: 参数模型类
        :param key_list: 需添加的字段名称列表
        :param value_key_list: 字段名称列表
        :param instance: 返回数据字典
        :param many: 多值的字符串列表
        :return: 返回数据字典
        """
        for i, value_key in enumerate(value_key_list):
            value = instance[key_list[i]]
            dict = {
                value_key: value
            }

            if key_list[i] in many:
                ret_list = []
                for val in utils.list_str_2_list(value):
                    dict[value_key] = val
                    ret_list.append(getattr(obj.objects.filter(**dict).first(), show_key))
                instance[key_list[i] + '_name'] = ', '.join(ret_list)
            else:
                instance[key_list[i] + '_name'] = getattr(obj.objects.filter(**dict).first(), show_key)
        return instance

    @staticmethod
    def add_area_value_to_instance(obj, key_list, param_key, instance):
        """
        为地区id添加翻译
        :param obj: 地区模型对象
        :param key_list: 需添加的字段名称列表
        :param param_key: 地区名称字段
        :param instance: 返回数据字典
        :return: 返回数据字典
        """
        for key in key_list:
            if instance[key]:
                instance[key + '_name'] = getattr(obj.objects.get(id=instance[key]), param_key)
        return instance

    @staticmethod
    def init_serializer(obj):
        """
        初始化序列化字段
        :param obj:
        :return:
        """
        try:
            # obj = IllegalSerializer
            __obj = obj.__dict__

            _model_obj = __obj.get('Meta').model  # serializer -> Meta -> model
            _model_fields = copy.deepcopy(_model_obj._meta.fields)  # model -> fields'

            _serializer_fields_tuple = __obj.get('Meta').fields  # serializer -> Meta -> fields
            _declared_fields_ordered_dict = __obj.get('_declared_fields')  # serializer -> fields
            _declared_fields_name_list = __obj.get('_declared_fields').keys()  # serializer已经编写好的字段

            # print('serializer -> Meta -> model', _model_obj)
            # print('serializer -> Meta -> fields', _serializer_fields_tuple)
            # print('serializer -> fields', _declared_fields_ordered_dict)
            # print('serializer -> fields', _declared_fields_ordered_dict['shop_name'].__dict__)

            # from apps.record.models import PushRecord
            # if _model_obj == PushRecord:
            #
            #     for i in [a for a in _model_obj._meta.fields]:
            #         print('-'*10, i)
            # print('-' * 10, _name)

            for _model_field in _model_obj._meta.fields:
                _model_type = type(_model_field)  # 字段类型
                _model_field_dict = _model_field.__dict__  # model -> field -> __dict__
                _name = _model_field_dict.get('name')  # 字段名称

                if _name not in _serializer_fields_tuple: continue  # 字段不在fields 中
                if _name in _declared_fields_name_list: continue  # serializer已经编写好的字段

                # print('model -> field', type(_model_field))
                # print('model -> field -> __dict__', _model_field_dict)
                """
                {'unique_for_year': None, 
                'model': <class 'apps.illegal.models.Illegal'>, 
                'error_messages': {'unique': '具有 %(field_label)s 的 %(model_name)s 已存在。', 'invalid': '’%(value)s‘ 必须为整数。', 'invalid_choice': '值%(value)r 不是有效选项。', 'null': '这个值不能为 null。', 'unique_for_date': '%(field_label)s 必须在 %(date_field_label)s 字段查找类型为 %(lookup_type)s 中唯一。', 'blank': '此字段不能为空。'}, 
                'db_tablespace': '', 
                'help_text': '',
                'default': <class 'django.db.models.fields.NOT_PROVIDED'>, 
                'null': False, 
                '_validators': [], 
                'blank': True, 
                '_verbose_name': 'ID', 
                'db_column': None, 
                '_unique': False, 
                'name': 'id', 
                'unique_for_date': None, 
                'remote_field': None, 
                'max_length': None, 
                'db_index': False, 
                'verbose_name': 'ID', 
                '_error_messages': None, 
                'column': 'id', 
                'concrete': True, 
                'is_relation': False, 
                'editable': True, 
                'attname': 'id', 
                'auto_created': True, 
                'choices': [], 
                'primary_key': True,
                'serialize': False, 
                'unique_for_month': None, 
                'creation_counter': -21}
                """
                _primary_key = _model_field_dict.get('primary_key')  # 是否主键

                _verbose_name = _model_field_dict.get('verbose_name')  # 详细的名称
                _help_text = _model_field_dict.get('help_text')  # 帮助说明
                _max_length = _model_field_dict.get('max_length')  # 最大长度
                _min_length = _model_field_dict.get('min_length')  # 最小长度
                _default = _model_field_dict.get('default')  # <class 'django.db.models.fields.NOT_PROVIDED'>
                _related_fields = _model_field_dict.get('_related_fields')  # 外键对象
                _choices = _model_field_dict.get('choices')  # 选项
                _name = _model_field_dict.get('name')  # 字段名称
                _obj_name = _model_obj._meta.object_name  # 类名

                _required = False
                _read_only = False
                _write_only = False

                if _primary_key or _related_fields: continue  # 主键外键不处理  跳过

                # 读取json文件配置required read_only write_only
                _json_dict = __class__.get_json_dict()
                _type = _json_dict[_obj_name]['fields'][_name]
                if _type == 'required':
                    _required = True
                elif _type == 'read_only':
                    _read_only = True
                elif _type == 'write_only':
                    _write_only = True
                elif _type == 'write_only':
                    _write_only = True
                _serializer_field = __class__.get_serializer_model(_model_field, _verbose_name, _help_text, _max_length,
                                                                   _min_length, _default, _choices, _required,
                                                                   _read_only,
                                                                   _write_only)  # 模型字段转换成序列字段
                if _serializer_field:
                    _declared_fields_ordered_dict[_name] = _serializer_field  # 格式 暂时不知道有什么用

            # print('serializer -> fields -> new', _declared_fields_ordered_dict)
            # print('-'*20)
            # print('serializer -> fields', _declared_fields_ordered_dict['state'].__dict__)

            # print(obj._declared_fields)
            obj._declared_fields = _declared_fields_ordered_dict
            # print(obj._declared_fields)
            return obj
        except:
            return obj

    @staticmethod
    def get_serializer_model(model_field, label, help_text, max_length, min_length, default, choices, required,
                             read_only, write_only):
        """
        将模型字段对象转成序列化字段
        :param model_field: 模型字段对象
        :param label: 标题
        :param help_text: 帮助
        :param max_length: 最大长度
        :param min_length: 最小长度
        :param default: 默认值
        :param choices: 选项
        :param required: 选项
        :param read_only: 选项
        :param write_only: 选项
        :return: 序列化字段对象
        """
        from django.db.models.fields import AutoField, CharField, DateTimeField, DateField, BooleanField, \
            IntegerField
        from django.db.models import fields
        from django.db.models.fields.files import ImageField
        from django.db.models.fields.related import ForeignKey
        from rest_framework import serializers
        from django.db.models.fields import NOT_PROVIDED  # 未设默认值

        _serializer_field = None
        serializer_field = None

        _field_list = [
            (AutoField, serializers.IntegerField),
            (IntegerField, serializers.IntegerField),
            (CharField, serializers.CharField),
            (DateTimeField, serializers.DateTimeField),
            (DateField, serializers.DateField),
            (BooleanField, serializers.BooleanField),
            (ImageField, serializers.ImageField),
            (ForeignKey, serializers.PrimaryKeyRelatedField),
            (fields.URLField, serializers.URLField),
        ]

        _is_choice_field = False
        for field_class, serializer_class in _field_list:  # 替换model field 为 serializer field
            if isinstance(model_field, field_class):
                _serializer_field = serializer_class
                break
        else:
            print('字段类型未配置:', model_field)

        if choices and isinstance(model_field, CharField):  # 判断是否有选项
            _serializer_field = serializers.ChoiceField
            _is_choice_field = True

        if isinstance(model_field, fields.URLField):  # 判断是否URL  会误认为char
            _serializer_field = serializers.URLField

        if _serializer_field:
            _kwargs = {}

            _kwargs['label'] = label
            _kwargs['help_text'] = help_text

            if not _is_choice_field:
                _max_length = max_length
                _min_length = min_length
                if max_length:
                    _kwargs['max_length'] = max_length
                else:
                    _max_length = 1000
                if min_length:
                    _kwargs['min_length'] = min_length
                else:
                    _min_length = 0
            else:
                _max_length = 1000
                _min_length = 0

            _kwargs['error_messages'] = __class__.get_error_messages(label, _max_length, _min_length)

            if choices: _kwargs['choices'] = choices

            flag = True
            try:
                if isinstance(default(), NOT_PROVIDED): flag = False
            except:
                flag = True
            if flag:
                _kwargs['default'] = default
            elif required:
                _kwargs['required'] = required
            else:
                _kwargs['required'] = required

            if write_only:
                _kwargs['write_only'] = write_only
            elif read_only:
                _kwargs['read_only'] = read_only

            serializer_field = _serializer_field(**_kwargs)

        return serializer_field

    @staticmethod
    def get_serializer_item(field_name, obj, exclude=()):
        # from django.db.models.fields import NOT_PROVIDED  # 未设默认值

        _model_fields = obj._meta.fields
        ret_dict = {
            'label': '',
            'help_text': '',
            'error_messages': '',
        }

        # for _model_field in _model_fields:
        # _model_type = type(_model_field)  # 字段类型
        # _model_field_dict = _model_field.__dict__  # model -> field -> __dict__
        #
        # _name           = _model_field_dict.get('name')  # 字段名称
        # if _name != field_name: continue
        # _verbose_name = _model_field_dict.get('verbose_name')  # 详细的名称
        # _help_text = _model_field_dict.get('help_text')  # 帮助说明
        # _max_length = _model_field_dict.get('max_length')  # 最大长度
        # _min_length = _model_field_dict.get('min_length')  # 最小长度
        # # _primary_key    = _model_field_dict.get('primary_key')  # 是否主键
        # # _default        = _model_field_dict.get('default')  # <class 'django.db.models.fields.NOT_PROVIDED'>
        # # _related_fields = _model_field_dict.get('_related_fields')  # 外键对象
        # # _choices        = _model_field_dict.get('choices')  # 选项

        _obj_name = obj.__name__  # 类名

        # 读取json文件配置required read_only write_only
        _json_dict = __class__.get_json_dict()

        if _obj_name == 'BaseModel':  # 基类
            _first_key = list(_json_dict.keys())[0]
            _verbose_name = _json_dict[_first_key]['fields'][field_name + '_0_label']  # 详细的名称
            _help_text = _json_dict[_first_key]['fields'][field_name + '_0_help']  # 帮助说明
            _max_length = _json_dict[_first_key]['fields'][field_name + '_0_max']  # 最大长度
            _min_length = _json_dict[_first_key]['fields'][field_name + '_0_min']  # 最小长度

        else:
            _verbose_name = _json_dict[_obj_name]['fields'][field_name + '_0_label']  # 详细的名称
            _help_text = _json_dict[_obj_name]['fields'][field_name + '_0_help']  # 帮助说明
            _max_length = _json_dict[_obj_name]['fields'][field_name + '_0_max']  # 最大长度
            _min_length = _json_dict[_obj_name]['fields'][field_name + '_0_min']  # 最小长度

        ret_dict['label'] = _verbose_name
        ret_dict['help_text'] = _help_text
        if 'max_length' not in exclude:
            if not _max_length:
                _max_length = 1000
            else:
                ret_dict['max_length'] = _max_length
        if 'min_length' not in exclude:
            if not _min_length:
                _min_length = 0
            else:
                ret_dict['min_length'] = _min_length
        ret_dict['error_messages'] = __class__.get_error_messages(_verbose_name, _max_length, _min_length, exclude=exclude)

        return ret_dict

    @staticmethod
    def get_json_dict(path='fields.json'):
        """
        获取模型字段信息
        :param path: json文件路径
        :return: 字典
        """
        _path = path
        if not os.path.exists(_path):
            auto_create_model_fields_2_file(__class__.CLASS_LIST)

        with open(_path, 'r', encoding='utf-8') as f:
            json_dict = json.load(f)

        return json_dict

    @staticmethod
    def get_model_info(obj_name, field_name):
        """
        根据类名和字段名称获取信息
        :param obj_name:
        :param field_name:
        :return:
        """
        # 读取json文件配置required read_only write_only
        _json_dict = __class__.get_json_dict()

        ret_dict = {}

        ret_dict['label'] = _json_dict[obj_name]['fields'][field_name + '_0_label']  # 详细的名称
        ret_dict['help'] = _json_dict[obj_name]['fields'][field_name + '_0_help']  # 帮助说明
        ret_dict['max'] = _json_dict[obj_name]['fields'][field_name + '_0_max']  # 最大长度
        ret_dict['min'] = _json_dict[obj_name]['fields'][field_name + '_0_min']  # 最小长度
        return ret_dict

    @staticmethod
    def get_extra_kwargs(model, exclude=(), read_only_fields=(), no_required_fields=(), write_only_fields=(),
                         validators=None, style=None, default=None):
        """
        自动生成序列化而外参数
        :param model: 模型对象
        :param exclude: 剔除字段
        :param read_only_fields: 只读字段
        :param no_required_fields: 非必填字段
        :param write_only_fields: 只写字段
        :param validators: 补充校验
        :param style: 字段风格
        :return:
        """
        from django.db.models.fields import NOT_PROVIDED
        # 返回的而外参数字典
        ret_dict = {}
        # 获取模型字段列表并遍历
        for _field in model._meta.fields:
            # 获取字段名称
            _name = _field.name
            # 判断字段是否只读或剔除 跳过
            if _name in (exclude + read_only_fields): continue
            # 拼接而外参数
            ret_dict[_name] = {}
            # label 字段中文解释
            ret_dict[_name]['label'] = _field.verbose_name
            # help_text 帮助信息
            ret_dict[_name]['help_text'] = _field.help_text
            # error_messages 错误消息提示
            _error_messages = _field.error_messages
            _error_messages['blank'] = '%(verbose_name)s, 不能为空' % _field.__dict__
            _error_messages['null'] = '%(verbose_name)s, 不能为null' % _field.__dict__
            if _field.max_length:
                _error_messages['max_length'] = '%(verbose_name)s, 最大长度不能超过%(max_length)d' % _field.__dict__
            if 'min_length' in _field.__dict__.keys() and _field.min_length:
                _error_messages['min_length'] = '%(verbose_name)s, 最小长度不能少于%(min_length)d' % _field.__dict__
            # 是否只写
            if _name in write_only_fields:
                ret_dict[_name]['write_only'] = True  # 只写

            # 判断是否有默认值
            _has_default = not isinstance(_field.default(), NOT_PROVIDED) if callable(_field.default) else True
            # 是否必填 不能为空 不是非必填 没有默认值
            if not _field.null \
                    and _name not in no_required_fields \
                    and not _has_default:
                ret_dict[_name]['required'] = True  # 必填
                _error_messages['required'] = '%(verbose_name)s, 为必填' % _field.__dict__
            else:
                ret_dict[_name]['required'] = False  # 非必填
            # 数据格式非法
            # _error_messages['invalid'] = '%(verbose_name)s, 数据无效' % _field.__dict__
            # _error_messages['invalid'] = _field.error_messages.get('invalid')
            # 将错误提示信息回填
            ret_dict[_name]['error_messages'] = _error_messages
            # 而外校验
            if validators:
                # 获取而外校验字段名称
                _validators_keys = validators.keys()
                if _name in _validators_keys:
                    # 赋值补充校验
                    ret_dict[_name]['validators'] = validators[_name]
            # 字段风格
            if style:
                # 获取风格字段名称
                _style_keys = style.keys()
                if _name in _style_keys:
                    # 赋值字段风格
                    ret_dict[_name]['style'] = style[_name]
            # 默认值
            if default:
                _default_keys = default.keys()
                if _name in _default_keys:
                    # 赋值默认值
                    ret_dict[_name]['default'] = default[_name]
                    print(default[_name])

        return ret_dict


class MyBaseSerializer(serializers.Serializer):
    # create_time = serializers.DateTimeField(read_only=True,
    #                                         **SerializerUtil.get_serializer_item('create_time', BaseModel))
    # update_time = serializers.DateTimeField(read_only=True,
    #                                         **SerializerUtil.get_serializer_item('update_time', BaseModel))
    # is_delete = serializers.BooleanField(read_only=True, **SerializerUtil.get_serializer_item('is_delete', BaseModel))

    class Meta:
        abstract = True
