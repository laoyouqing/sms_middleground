from django.db import models
from django.contrib.auth.models import AbstractUser

from my_base.base_model import BaseModel
from my_utils import enum


# Create your models here.
class Report(BaseModel):
    """
    数据统计表
    """
    chart_json = models.CharField(max_length=1000, blank=True, null=True, verbose_name='数据json字符串',
                                  help_text='统计后的数据集合')
    date = models.DateField(verbose_name='日期', help_text='统计以天为单位')
    success = models.IntegerField(default=0, verbose_name='成功数', help_text='当日成功数')
    fail = models.IntegerField(default=0, verbose_name='失败数', help_text='当日失败数')
    error = models.IntegerField(default=0, verbose_name='错误数', help_text='当日调试数')
    debug = models.IntegerField(default=0, verbose_name='调试数', help_text='当日错误数')
    warn = models.IntegerField(default=0, verbose_name='预警数', help_text='当日预警数')
    total = models.IntegerField(default=0, verbose_name='总数', help_text='当日总数(成功+失败)')
    real_total = models.IntegerField(default=0, verbose_name='实际总数', help_text='当日总数+调试+错误+预警')
    success_rate = models.DecimalField(default=0.0000, max_digits=5, decimal_places=4, verbose_name='成功率', help_text='当日成功率(成功/总数)')
    real_success_rate = models.DecimalField(default=0.0000, max_digits=5, decimal_places=4, verbose_name='实际成功率',
                                            help_text='当日实际成功率((成功+调试+预警)/实际总数)')
    fail_rate = models.DecimalField(default=0.0000, max_digits=5, decimal_places=4, verbose_name='失败率', help_text='当日失败率(失败/总数)')
    real_fail_rate = models.DecimalField(default=0.0000, max_digits=5, decimal_places=4, verbose_name='实际失败率',
                                         help_text='当日实际失败率((失败+错误)/实际总数)')

    class Meta:
        db_table = 'report'
        verbose_name = '数据统计'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.date


REPORT_C_LIST = [Report]
