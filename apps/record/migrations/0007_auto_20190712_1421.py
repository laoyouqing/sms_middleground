# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-07-12 14:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record', '0006_auto_20190712_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pushrecord',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, help_text='精确到秒', verbose_name='创建时间'),
        ),
    ]
