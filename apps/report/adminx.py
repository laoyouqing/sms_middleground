#!/usr/bin/env python
# encoding: utf-8

import xadmin

from xadmin import views
from apps.report.models import Report
from my_utils import utils


class ReportAdmin(object):
    list_display = utils.get_model_fields(Report)


xadmin.site.register(Report, ReportAdmin)
