# coding:utf-8

from django.db import models

# Create your models here.

class Server(models.Model):
    supplier        = models.IntegerField(null=True)
    manufacturers   = models.CharField(max_length=50, null=True)
    manufacture_date= models.DateField(null=True)
    server_type     = models.CharField(max_length=20, null=True)
    sn              = models.CharField(max_length=60, db_index=True, null=True)
    idc_id          = models.CharField(max_length=20, db_index=True,null=True)
    cabinet_id      = models.IntegerField(null=True)
    cabinet_pos     = models.CharField(max_length=20, null=True)
    expire          = models.DateField(null=True)
    os              = models.CharField(max_length=50, null=True)
    hostname        = models.CharField(max_length=50, db_index=True, null=True)
    inner_ip        = models.CharField(max_length=32, db_index=True, null=True)
    mac_address     = models.CharField(max_length=50, null=True)
    ip_info         = models.CharField(max_length=255, null=True)
    server_cpu      = models.CharField(max_length=250, null=True)
    server_disk     = models.CharField(max_length=100, null=True)
    server_mem      = models.CharField(max_length=100, null=True)
    status          = models.CharField(max_length=100,db_index=True, null=True)
    remark          = models.TextField(null=True)
    last_op_time    = models.DateTimeField(null=True)
    last_op_people  = models.IntegerField(null=True)
    service_id      = models.IntegerField(db_index=True, null=True)
    server_purpose  = models.IntegerField(db_index=True, null=True)
    trouble_resolve = models.IntegerField(null=True)
    op_interface_other = models.IntegerField(null=True)
    dev_interface   = models.IntegerField(null=True)
    check_update_time = models.DateTimeField(null=True)
    vm_status       = models.IntegerField(db_index=True, null=True)
    uuid            = models.CharField(max_length=100, db_index=True,null=True)

    def __str__(self):
        return self.hostname

    class Meta:
        db_table = 'resources_server'
        ordering = ['id']


class Status(models.Model):
    name            = models.CharField(max_length=100, unique=True, db_index=True)

    class Meta:
        db_table = "resources_status"