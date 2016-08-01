# coding:utf-8
import logging

from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator



class UserLoginView(TemplateView):
    """
        同步主机到zabbix
    """
    template_name = "resources/user/login.html"


    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request):
        ret = {"status": 0}
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("/resources/index/")
            else:
                ret['status'] = 2
                ret['errmsg'] = "该用户禁止登陆"
        else:
            ret['status'] = 1
            ret['errmsg'] = "用户名或密码错误"
        return render(request, settings.ACTION_JUMP, {"message": ret, "next_url": "/login/"})

class UserLogoutView(View):

    @method_decorator(login_required)
    def get(self, request):
        logout(request)
        return redirect("/login/")