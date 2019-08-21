from django.db import models
from my_utils import enum


class BaseManager(models.Manager):
    """
    管理类
    """

    def no_delete_all(self):
        return self.get_queryset().filter(is_delete=False)


class BaseModel(models.Model):
    """
    模型抽象基类
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='精确到秒')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='精确到秒')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记', help_text='逻辑删除标识')

    objects = BaseManager()

    class Meta:
        # 说明是一个抽象模型类
        abstract = True
