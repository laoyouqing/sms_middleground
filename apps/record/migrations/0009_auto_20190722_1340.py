# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-07-22 13:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20190719_1057'),
        ('record', '0008_auto_20190719_0940'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmsSign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='精确到秒', verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='精确到秒', verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, help_text='逻辑删除标识', verbose_name='删除标记')),
                ('sign_name', models.CharField(help_text='签名名称', max_length=30, verbose_name='签名名称')),
                ('sign_source', models.SmallIntegerField(choices=[(0, '企事业单位的全称或简称'), (1, '工信部备案网站的全称或简称'), (2, 'APP应用的全称或简称'), (3, '公众号或小程序的全称或简称'), (4, '电商平台店铺名的全称或简称'), (5, '商标名的全称或简称')], help_text='0：企事业单位的全称或简称。1：工信部备案网站的全称或简称。2：APP应用的全称或简称。3：公众号或小程序的全称或简称。4：电商平台店铺名的全称或简称。5：商标名的全称或简称', verbose_name='签名来源')),
                ('remark', models.CharField(help_text='请在申请说明中详细描述您的业务使用场景，申请工信部备案网站的全称或简称请在此处填写域名，长度不超过200个字符', max_length=30, verbose_name='申请说明')),
                ('action', models.CharField(blank=True, help_text='系统规定参数', max_length=30, null=True, verbose_name='系统规定参数')),
                ('access_key_id', models.CharField(blank=True, help_text='阿里主账号AccessKey的ID', max_length=30, null=True, verbose_name='AccessKeyId')),
                ('file_suffix', models.ImageField(blank=True, help_text='签名的证明文件格式，支持上传多张图片。当前支持jpg、png、gif或jpeg格式的图片。个别场景下，申请签名需要上传证明文件。', null=True, upload_to='sign', verbose_name='签名证明')),
                ('file_contents', models.ImageField(blank=True, help_text='签名的质证明文件经base64编码后的字符串。图片不超过2 MB。个别场景下，申请签名需要上传证明文件。', null=True, upload_to='sign', verbose_name='签名质证明文件')),
                ('secret_key', models.CharField(blank=True, help_text='客户注册时生成的唯一密匙', max_length=36, null=True, verbose_name='密钥')),
                ('client', models.ForeignKey(blank=True, help_text='所属客户', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='my_sign', to='user.Client', verbose_name='所属客户')),
            ],
            options={
                'verbose_name_plural': '短信签名',
                'verbose_name': '短信签名',
                'db_table': 'sms_sign',
            },
        ),
        migrations.CreateModel(
            name='SmsTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='精确到秒', verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='精确到秒', verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, help_text='逻辑删除标识', verbose_name='删除标记')),
                ('template_type', models.SmallIntegerField(choices=[(0, '验证码'), (1, '短信通知'), (2, '推广短信'), (3, '国际/港澳台消息')], help_text='0：验证码。1：短信通知。2：推广短信。3：国际/港澳台消息。', verbose_name='短信类型')),
                ('template_name', models.CharField(help_text='长度为1~30个字符', max_length=30, verbose_name='模板名称')),
                ('template_Content', models.CharField(help_text='长度为1~500个字符', max_length=500, verbose_name='模板内容')),
                ('remark', models.CharField(help_text='请在申请说明中描述您的业务使用场景，长度为1~100个字符。', max_length=100, verbose_name='申请说明')),
                ('action', models.CharField(blank=True, help_text='系统规定参数', max_length=30, null=True, verbose_name='系统规定参数')),
                ('access_key_id', models.CharField(blank=True, help_text='阿里主账号AccessKey的ID', max_length=30, null=True, verbose_name='AccessKeyId')),
                ('secret_key', models.CharField(blank=True, help_text='客户注册时生成的唯一密匙', max_length=36, null=True, verbose_name='密钥')),
                ('client', models.ForeignKey(blank=True, help_text='所属客户', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='my_template', to='user.Client', verbose_name='所属客户')),
            ],
            options={
                'verbose_name_plural': '短信模板',
                'verbose_name': '短信模板',
                'db_table': 'sms_template',
            },
        ),
        migrations.AlterField(
            model_name='pushrecord',
            name='result',
            field=models.CharField(blank=True, choices=[('success', '成功'), ('fail', '失败'), ('error', '错误'), ('debug', '测试'), ('batch', '批量')], help_text='success: 成功, fail: 失败, error: 错误', max_length=30, null=True, verbose_name='推送结果'),
        ),
    ]
