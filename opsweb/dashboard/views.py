# coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index_view(request):
    return render(request,"resources/index.html", {"title": "首页"})
