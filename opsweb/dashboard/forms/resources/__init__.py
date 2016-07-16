# coding:utf-8
from django import forms

class StatusForm(forms.Form):
    name = forms.CharField(required=True)