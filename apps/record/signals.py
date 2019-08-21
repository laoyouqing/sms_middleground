# -*- coding: utf-8 -*-
from django.db.models.signals import post_save, post_delete, post_migrate
from django.dispatch import receiver

from my_base import base_signals
from my_utils.auto_utils import auto_create_model_fields_2_file


@receiver(post_migrate)
def creat_fields_json(sender, **kwargs):
    """
    监听migrate信号
    :param sender:
    :param kwargs:
    :return:
    """
    base_signals.creat_fields_json(sender, **kwargs)