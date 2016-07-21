# coding:utf-8
import time
import random
import logging
from django.conf import settings
from zabbix_client import ZabbixServerProxy
from opsweb.settings import ZABBIX_URL, ZABBIX_USER, ZABBIX_PASS
from dashboard.models import Zabbix as zabbix_db
from dashboard.models import Server


logger = logging.getLogger("django")


class Zabbix():
    def __init__(self):
        self.zb = ZabbixServerProxy(ZABBIX_URL)
        self.zb.user.login(user=ZABBIX_USER, password=ZABBIX_PASS)

    def get_hosts(self):
        return self.zb.host.get(output=['hostid', 'host'])

    def get_interface(self,ids):
        data = self.zb.hostinterface.get(hostids=ids, output=['hostid', 'ip'])
        ret = {}
        for d in data:
            ret[d['hostid']] = d['ip']
        return ret

    def get_hostgroup(self):
        data = self.zb.hostgroup.get(output=['groupid', 'name'])
        return data

    def get_template(self,ids):
        ret = self.zb.template.get(hostids=ids,output=['templateid', 'name'])
        return ret

    def link_template(self,hostids, templates):
        ret = []
        for hostid in hostids:
            linked_templates_ids = [t['templateid'] for t in self.get_template(hostid)]
            linked_templates_ids.extend(templates)
            ret.append(self._link_template(hostid, linked_templates_ids))
        return ret


    def _link_template(self, hostid, templateids):
        templates = []
        for id in templateids:
            templates.append({"templateid": id})
        try:
            ret = self.zb.host.update(hostid=hostid,templates=templates)
        except Exception as e:
            return e.args
        return ret

    def unlink_template(self, hostid, templateid):
        return self.zb.host.update(hostid= hostid,templates_clear=[{"templateid":templateid}])

    def create_hosts(self, params):
        return self.zb.host.create(**params)

    def create_maintenance(self, hostids, active_since, active_till):
        data = {'name':random.randint(1,100000),
                'active_since': active_since,
                'active_till': active_till,
                'hostids':hostids,
                'timeperiods':[
                        {
                            "timeperiod_type": 0,
                            "start_date":active_since,
                            "period":  active_till
                        }
                    ]
                }
        try:
            ret = self.zb.maintenance.create(data)
        except Exception as e:
            ret = {'error': e.args}
        return ret

    def get_maintenance(self):
        return self.zb.maintenance.get(output=['active_since','active_till','maintenanceid'],selectHosts=['name'])

    def del_maintenance(self, maintenanceid):
        return self.zb.maintenance.delete(maintenanceid)

    def __del__(self):
        self.zb.user.logout()

    def rsync_zabbix_to_zbhost(self):
        """
            将zabbix里的监控主机同步到缓存表中
        :return:
        """
        zb_hosts = self.get_hosts()
        zb_hosts_ids = [zb.get('hostid') for zb in zb_hosts]
        zb_hosts_interface = self.get_interface(zb_hosts_ids)
        for host in zb_hosts:
            try:
                h = zabbix_db.objects.get(hostid__exact=host['hostid'])
            except zabbix_db.DoesNotExist:
                host['ip'] = zb_hosts_interface[host['hostid']]
                host['updatetime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                zbhost = zabbix_db(**host)
                zbhost.save()

    def rsync_server_to_zbhost(self):
        """
            将服务器信息同步到缓存表中
        :return:
        """
        host = zabbix_db.objects.all()
        servers = Server.objects.filter(inner_ip__in=[h.ip for h in host])
        servers_info = {}
        for s in servers:
            servers_info[s.inner_ip] = s.id

        data = {
            'updatetime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        }
        host_not_in_cmdb = []
        for h in host:
            if not h.cmdb_hostid:
                try:
                    data["cmdb_hostid"] = servers_info[h.ip]
                    zabbix_db.objects.filter(id__exact=h.id).update(**data)
                except KeyError:
                    host_not_in_cmdb.append(h.ip)
        #send_email(settings.ADMIN_EMAIL, "zabbix 缓存同步失败","\n".join(host_not_in_cmdb))



def create_zabbix_hosts(hostids, groupid):
    servers = Server.objects.filter(id__in=hostids).all()
    zb = Zabbix()
    ret = []
    for host in servers:
        data = {
            "host": host.hostname,
            "interfaces": [
                {
                    "type": 1,
                    "main": 1,
                    "useip": 1,
                    "ip": host.inner_ip,
                    "dns": "",
                    "port": "10050"
                }
            ],
            "groups": [
                {
                    "groupid": groupid
                }
            ]
        }
        ret.append(zb.create_hosts(data))
    return ret


def get_zbhostid(data):
    ret = []
    for d in data:
        ret.append(d['hostid'])
    return ret





def get_zabbix_data(hosts):
    """
    获取zabbix的机器以及模板信息
    :return:
    """
    ret = []
    zb = Zabbix()
    zabbix_data = zabbix_db.objects.filter(cmdb_hostid__in=[h.id for h in hosts])
    for zb_host in zabbix_data:
        tmp = {}
        tmp['hostname'] = zb_host.host
        tmp['templates'] = zb.get_template(ids=zb_host.hostid)
        tmp['hostid'] = zb_host.hostid
        ret.append(tmp)
    return ret





def create_maintenance(hostids, active_since, active_till):
    ret = []
    zb = Zabbix()
    for hostid in hostids:
        # 增加维护
        tmp_err = []
        try:
            r = zb.create_maintenance([hostid], active_since, active_till)
            # {'maintenanceids': ['22']}
            maintenanceid = r['maintenanceids'][0]
        except Exception as e:
            logger.error("维护zabbix失败失败: {}".format(e.args))
            tmp_err.append(e.args)
            ret.append({hostid: tmp_err})
            continue
        update_data = {
            "hostid": hostid,
            "maintenance_status": 1,
            "maintenanceid": maintenanceid,
            "maintenance_from": active_since,

        }
        try:
            r_m = zb.zb.host.update(update_data)
            if r_m['hostids']:
                logger.debug("创建主机成功: {}".format(r_m))

        except Exception as e:
            logger.error("更新状态失败: {}".format(e.args))
            tmp_err.append(e.args)
            ret.append({hostid: tmp_err})
    if ret:
        return ret
    return True


def rsync_zabbix_cache():
    zabbix_db.objects.all().delete()
    zb = Zabbix()
    zb.rsync_zabbix_to_zbhost()
    zb.rsync_server_to_zbhost()