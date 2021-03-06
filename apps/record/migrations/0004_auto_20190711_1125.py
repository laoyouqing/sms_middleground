# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-07-11 11:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record', '0003_remove_pushrecord_equipment'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushrecord',
            name='template_code',
            field=models.CharField(default='SMS_125020249', help_text='阿里云短信模板id', max_length=30, verbose_name='短信模板id'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pushrecord',
            name='sign_name',
            field=models.CharField(blank=True, help_text='短信签名', max_length=30, null=True, verbose_name='短信签名'),
        ),
    ]
