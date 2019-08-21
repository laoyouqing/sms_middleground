#!/usr/bin/env python
# encoding: utf-8

import xadmin

from xadmin import views
from apps.record.models import PushRecord, RechargeRecord
from my_utils import utils


class PushRecordAdmin(object):
    list_display = utils.get_model_fields(PushRecord)


class RechargeRecordAdmin(object):
    list_display = utils.get_model_fields(RechargeRecord)


xadmin.site.register(PushRecord, PushRecordAdmin)
xadmin.site.register(RechargeRecord, RechargeRecordAdmin)
