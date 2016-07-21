#coding:utf-8

import time
import json
import logging

from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, ListView, View
from django.http import Http404
from django.conf import settings

from dashboard.models import Server, Zabbix as zb_host

from . import Zabbix, create_zabbix_hosts, get_zabbix_data, rsync_zabbix_cache
from dashboard.resources.server import  get_treeview_data





log = logging.getLogger(__name__)


class ZabbixHostGroupListView(View):

    def get(self, request):
        zb = Zabbix()
        hostgroups = zb.get_hostgroup()
        return HttpResponse(json.dumps(hostgroups),content_type='application/json')



class RsyncHostZabbix(TemplateView):
    """
        同步主机到zabbix
    """
    template_name = "resources/zabbix/host_rsync.html"


    def get(self, request, *args, **kwargs):
        zabbix_hosts = zb_host.objects.all()
        hostids = [zb.cmdb_hostid for zb in zabbix_hosts if zb.cmdb_hostid is not None]
        servers = Server.objects.exclude(id__in=hostids).exclude(vm_status__exact=2)
        zb = Zabbix()
        hostgroups = zb.get_hostgroup()
        return render(request, self.template_name, {"hostlist": servers, "hostgroups": hostgroups})

    def post(self, request):
        ret = {"status":0, 'errmsg':[]}
        hosts = request.POST.getlist("host")
        group = request.POST.get('group')
        data = create_zabbix_hosts(hostids=hosts, groupid=group)
        rsync_zabbix_cache()
        for zb_ret in data:
            if zb_ret.get("hostids", None):
                if not zb_ret["hostids"][0].isdigit():
                    ret['status'] = 1
                    ret['errmsg'].append("创建失败: {}".format(zb_ret["hostids"]))
            else:
                ret['status'] = 1
                ret['errmsg'].append(zb_ret)
        return render(request, settings.ACTION_JUMP, {"message": ret, "next_url": "/resources/monitor/zabbix/rsync/"})

class TemplateLinkView(TemplateView):
    template_name = "resources/zabbix/link_template.html"
    def get(self, request, *args, **kwargs):
        zb = Zabbix()
        data = get_treeview_data(idc=False)
        zb_templates = zb.zb.template.get(output=['templateid', 'name'])
        templates = [{"value": zb['templateid'], 'label': zb['name']} for zb in zb_templates]
        response_data = {
            'treeview': json.dumps(data),
            'templates': json.dumps(templates),
            "title": "zabbix 模板绑定",
            "show_monitor": True,
            "show_monitor_zabbix": True,
        }
        return render(request, self.template_name, response_data)

    def post(self, request):
        data = request.POST.dict()
        zb = Zabbix()
        # {'template_ids': '10102,10047', 'hostids': '10512,10508,10234,10509,10514,10226,10516,10231'}

        templateids = data['template_ids'].split(',')
        hostids = data['hostids'].split(',')
        ret_data = zb.link_template(hostids, templateids)

        # [{'hostids': ['10295']}]
        # ('Code: -32602, Message: Invalid params., Data: Template "Template ncfgroup basics" with item key "agent.hostname" already linked to host.',)

        for r in ret_data:
            try:
                hostids.remove(r.get('hostids', [])[0])
            except Exception as e:
                return HttpResponse(json.dumps(r))
        if hostids:
            return HttpResponse(json.dumps(hostids))
        return HttpResponse("1")

class TemplateUnLinkView(View):
    def post(self, request):
        data = request.POST.dict()
        # {'hostid': '10295', 'templateid': '10312'}
        zb = Zabbix()
        ret = zb.unlink_template(**data)
        # {'hostids': ['10295']}
        if isinstance(ret, dict) and ret.get('hostids')[0] == data['hostid']:
            return HttpResponse(1)
        else:
            return HttpResponse(json.dumps(ret))


class ZabbixHostTemplateView(View):
    def get(self, request):
        data = request.GET.dict()
        hosts = Server.objects.filter(**data)
        re = get_zabbix_data(hosts)
        return HttpResponse(json.dumps(re), content_type="applicate/json")



class RsyncZabbixCacheView(View):
    """
    同步zabbix 缓存
    """
    def post(self, request):
        ret = {"status": 0}
        rsync_zabbix_cache()
        return HttpResponse(json.dumps(ret), content_type="applicate/json")
