# coding:utf-8

import time
import json
import logging

from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, ListView, View
from django.http import Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from dashboard.models import Server, Status, Product, Idc


log = logging.getLogger(__name__)

class AutoReportingView(View):
    """
        服务器信息自动上报
    """

    @method_decorator(login_required)
    def post(self, request):
        data = request.POST.dict()
        data['check_update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        try:
            if Server.objects.get(uuid=data['uuid']):
                Server.objects.filter(uuid=data['uuid']).update(**data)
                return HttpResponse("200")
        except Exception as e:
            pass

        try:
            s = Server(**data)
            s.save()
        except Exception, e:
            log.error("服务器信息自动上报，添加时失败: {}".format(e.args))
        return HttpResponse("200")

class ServerListView(ListView):
    """
        服务器列表信息
    """
    template_name = "resources/server/server_list.html"
    model = Server
    context_object_name = "server_list"


    def get_context_data(self, **kwargs):
        context = super(ServerListView, self).get_context_data(**kwargs)
        context["title"] = "服务器列表信息"
        context['products'] = Product.objects.all()
        return context

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        response = super(ServerListView, self).get(request, *args, **kwargs)
        return response



class ServerModifyStatusView(TemplateView):

    template_name = "resources/server/server_modify_status.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        server_id = request.GET.get("server_id")

        if not server_id or not server_id.isalnum():
            raise Http404
        try:
            server = Server.objects.get(pk=server_id)
            status = Status.objects.all()
            return render(request, self.template_name, {"server": server, "statuses": status})
        except Server.DoesNotExist:
            raise Http404

    @method_decorator(login_required)
    def post(self, request):
        ret = {"status": 0}
        try:
            Server.objects.filter(pk=request.POST.get("id", 0)).update(status=request.POST.get("status",None))
            return render(request, settings.ACTION_JUMP, {"message": json.dumps(ret), "next_url": "/resources/server/list/"})
        except Exception, e:
            raise Http404

class ServerModifyProductView(TemplateView):

    template_name = "resources/server/server_modify_product.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        server_id = request.GET.get("server_id")

        if not server_id or not server_id.isalnum():
            raise Http404
        try:
            server = Server.objects.get(pk=server_id)
            products = Product.objects.all()
            return render(request, self.template_name, {"server": server, "products": products})
        except Server.DoesNotExist:
            raise Http404

    @method_decorator(login_required)
    def post(self, request):
        ret = {"status": 0}


        data = {
            "server_purpose": request.POST.get("server_purpose", 0),
            "service_id": request.POST.get("service_id", 0)
        }
        try:
            Server.objects.filter(pk=request.POST.get("id", 0)).update(**data)
            return render(request, settings.ACTION_JUMP, {"message": json.dumps(ret), "next_url": "/resources/server/list/"})
        except Exception, e:
            raise Http404



class Treeview():
    def __init__(self):
        self.idc_info = Idc.objects.all()
        self.product_info = Product.objects.all()
        self.data = []

    def get_child_node(self):
        ret = []
        state = {'disabled': 'false'}
        for p in filter(lambda x:  True if x.pid == 0 else False, self.product_info):
            node = {}
            node['text'] = p.service_name
            node['id'] = p.id
            node['type'] = 'service'
            node['icon'] = "glyphicon glyphicon-th"
            node['selectable'] = "false"
            #node['state'] = state
            node['nodes'] = self.get_grant_node(p.id)
            ret.append(node)
        return ret

    def get_grant_node(self, pid):
        ret = []
        for p in filter(lambda x :True if x.pid == pid else False, self.product_info):
            node = {}
            node['text'] = p.module_letter
            node['id'] = p.id
            node['type'] = 'product'
            node['icon'] = "glyphicon glyphicon-file"
            node['pid'] = pid
            ret.append(node)
        return ret

    def get(self,idc):
        child = self.get_child_node()
        if not idc:
            return child
        ret = []
        for idc in self.idc_info:
            node = {}
            node['text'] = idc.name
            node['id'] = idc.id
            node['type'] = 'idc'
            node['nodes'] = child
            ret.append(node)
        return ret




"""
    获取节点树信息
"""
def get_treeview_data(idc=True):
    treeview = Treeview()
    return treeview.get(idc)

