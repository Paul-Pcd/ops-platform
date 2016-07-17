# coding:utf-8
from django import forms

class StatusForm(forms.Form):
    name = forms.CharField(required=True)


class ProductForm(forms.Form):
    service_name    = forms.CharField(required=True)
    pid             = forms.IntegerField(required=True)
    module_letter   = forms.CharField(required=True)
    dev_interface   = forms.CharField(required=True)
    op_interface    = forms.CharField(required=True)