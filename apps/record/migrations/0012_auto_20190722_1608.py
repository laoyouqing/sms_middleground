# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-07-22 16:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record', '0011_auto_20190722_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='smstemplate',
            name='reason',
            field=models.CharField(blank=True, help_text='审核不通过具体原因', max_length=300, null=True, verbose_name='审核备注'),
        ),
        migrations.AddField(
            model_name='smstemplate',
            name='template_code',
            field=models.CharField(blank=True, help_text='阿里短信模板编号', max_length=30, null=True, verbose_name='模板编号'),
        ),
        migrations.AddField(
            model_name='smstemplate',
            name='template_status',
            field=models.SmallIntegerField(choices=[(0, '审核中'), (1, '审核通过'), (2, '审核失败，请在返回参数Reason中查看审核失败原因')], default=0, help_text='0：审核中。1：审核通过。2：审核失败，请在返回参数Reason中查看审核失败原因。', verbose_name='申请状态'),
        ),
    ]
