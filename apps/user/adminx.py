#!/usr/bin/env python
# encoding: utf-8

import xadmin

from xadmin import views
from apps.user.models import User, Client
from my_utils import utils


class ClientAdmin(object):
    list_display = utils.get_model_fields(Client)


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


class GlobalSettings(object):
    site_title = "锐掌短信中台后台"
    site_footer = "sms_middleground"
    menu_style = "accordion"


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(Client, ClientAdmin)
