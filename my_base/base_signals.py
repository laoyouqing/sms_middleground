import re
from django.db.models.signals import post_save, post_delete, post_migrate
from django.dispatch import receiver

from my_utils.auto_utils import auto_create_model_fields_2_file
from my_utils import utils


def suf_save_del_img(sender, instance=None, created=False, **kwargs):
    if not created:
        key_list = re.findall(r'\'(\w+)\':\s+<django.db.models.fields.files.Image.*?\s', str(sender.__dict__))  # 获取模型类中的图片字段
        for key, url in [(key, getattr(instance, key).url) for key in key_list if getattr(instance, key)]:  # 遍历对象的图片链接
            url_list = [getattr(obj, key).url for obj in sender.objects.all()]  # 获取数据库中所有图片路径
            name_list = [re.match(r'.*/(.*?)$', url).group(1) for url in url_list]  # 获取数据库所有图片路径的图片名称
            path = re.match(r'/?(.*/).*?$', url).group(1)  # 获取图片储存的文件夹路径
            utils.del_useless_file(path, name_list)  # 删除无用图片

def suf_delete_del_img(sender, instance=None, **kwargs):
    key_list = re.findall(r'\'(\w+)\':\s+<django.db.models.fields.files.Image.*?\s', str(sender.__dict__))  # 获取模型类中的图片字段
    for key, url in [(key, getattr(instance, key).url) for key in key_list if getattr(instance, key)]:  # 遍历对象的图片链接
        path = re.match(r'/?(.*/).*?$', url).group(1)  # 获取图片储存的文件夹路径
        file_name = re.match(r'/?.*/(.*?)$', url).group(1)  # 获取图片储存的文件夹路径
        utils.del_file(path, file_name)  # 删除无用图片

def creat_fields_json(sender, **kwargs):
    """
    监听migrate信号
    :param sender:
    :param kwargs:
    :return:
    """
    from apps.user.apps import UserConfig
    # from apps.param.apps import ParamConfig
    from apps.record.apps import RecordConfig
    from apps.report.apps import ReportConfig

    if sender.name in (RecordConfig.name, UserConfig.name, ReportConfig.name):
        _models = [models for models in sender.get_models()]
        auto_create_model_fields_2_file(_models)  # 创建字段json文件

        # if sender.name == ParamConfig.name:
        #     from apps.param.models import Param
        #     if Param.objects.all().count() < 1:
        #         Param.objects.create()  # 初始化参数数据