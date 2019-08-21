import json, os, copy, re
from collections import OrderedDict

def sort_dict(dict, reverse=False):
    """
    对字典进行排序并返回字典
    :param dict: 要排序的字典
    :param reverse: 是否倒叙
    :return:
    """
    _keys = sorted(dict.keys(), reverse=reverse)
    new_dict = OrderedDict()
    for _key in _keys:
        new_dict[_key] = dict[_key]
    return new_dict

def auto_create_model_fields_2_file(obj_list, to_path='./fields.json'):
    """
    自动生成模型字段文件
    :param path:
    :param file_name:
    :param class_name:
    :return:
    """
    data_dict = {}
    if os.path.exists(to_path):
        # print('文件存在')
        with open(to_path, 'r', encoding='utf-8') as f:
            data_dict = json.load(f, object_pairs_hook=OrderedDict)  # 有序

    # 提取有改动的数据形成新的dict备用
    # _new_dict = copy.deepcopy(data_dict)
    # for _key, _value in _new_dict.items():
        # print(_key)
        # for _field_key in _value['fields'].keys():
            # if _value['fields'][_field_key] == 'required':
                # del data_dict[_key]['fields'][_field_key]

    for _obj in set(obj_list):
        _obj_name = _obj._meta.object_name  # 类对象名称
        _verbose_name = _obj._meta.verbose_name  # 类对象中文名称
        _model_dict = data_dict.get(_obj_name)  # 获取文件中的类字段数据
        dict = _model_dict if _model_dict else {}

        dict['verbose_name'] = _verbose_name
        dict['fields'] = dict.get('fields') if dict.get('fields') else {}
        for key, name, model_field in [(_model_field.name, _model_field.verbose_name, _model_field) for _model_field in _obj._meta.fields]:
            # status = key + '_status'
            label = key + '_0_label'
            help = key + '_0_help'
            max_length = key + '_0_max'
            min_length = key + '_0_min'
            # if model_field.primary_key or model_field.__dict__.get('_related_fields'):  # 剔除主键和外键
            # if model_field.primary_key:  # 剔除主键
            #     if dict.get('fields').get(label):
            #         del dict['fields'][label]
            #     if dict.get('fields').get(help):
            #         del dict['fields'][help]
            #     continue

            if not dict['fields'].get(label):
                dict['fields'][label] = str(name)

            if not dict['fields'].get(key):
                if re.match(r'is_delete|update_time|create_time', key):
                    dict['fields'][key] = 'read_only'
                else:
                    if model_field.blank:
                        dict['fields'][key] = 'no_required'
                    else:
                        dict['fields'][key] = 'required'

            # if dict['fields'].get(status):
            #     del dict['fields'][status]

            dict['fields'][help] = str(model_field.help_text)  # 帮助内容

            max = None
            min = None
            if hasattr(model_field, 'max_length'):
                max = model_field.max_length

            if hasattr(model_field, 'min_length'):
                min = model_field.min_length

            dict['fields'][max_length] = max  # 最大长度
            dict['fields'][min_length] = min  # 最小长度

        dict = sort_dict(dict, reverse=True)  # 排序
        dict['fields'] = sort_dict(dict['fields'])  # 排序
        data_dict[_obj_name] = dict

    data_dict = sort_dict(data_dict)  # 排序
    _json_data = json.dumps(data_dict, ensure_ascii=False, indent=2)

    with open(to_path, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=2)
