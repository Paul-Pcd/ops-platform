# coding:utf-8
from __future__ import unicode_literals
import time
import logging
import json

from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, ListView, View
from django.db import IntegrityError
from django.conf import settings

from dashboard.forms.resources import StatusForm
from dashboard.models import Status



log = logging.getLogger(__name__)

class StatusAddView(TemplateView):

    template_name = "resources/server/status/status_add.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,{"title": "添加状态信息"})

    def post(self, request):
        ret = {"status": 0}

        status_from = StatusForm(request.POST)
        if status_from.is_valid():
            try:
                status = Status(**status_from.cleaned_data)
                status.save()
            except IntegrityError ,e:
                print e.args
                ret['status'] = 3
                ret['errmsg'] = "该记录已存在"
        else:
            ret['status'] = 1
            ret['errmsg'] = status_from.errors.as_json()
        return render(request, settings.ACTION_JUMP, {"message": json.dumps(ret), "next_url": "/resources/server/status/add/"})