# coding:utf-8
from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, ListView, View
from django.conf import settings
from django.core import serializers

from dashboard.models import Product
from dashboard.forms.resources import ProductForm


class ProductAddView(TemplateView):

    template_name = "resources/product/product_add.html"

    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(pid__exact=0)
        return render(request, self.template_name, {"products": products})

    def post(self, request):
        print request.POST


        ret = {"status": 0}
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                p = Product(**form.cleaned_data)
                p.save()
            except Exception, e:
                ret['status'] = 1
                ret['errmsg'] = e.args
        else:
            ret['status'] = 1
            ret['errmsg'] = form.errors.as_json()
        return render(request, settings.ACTION_JUMP, {"message": ret, "next_url": "/resources/product/add/"})

class ProductJsonResponse(View):
    def get(self, request):
        product = serializers.serialize('json', Product.objects.all())
        return HttpResponse(product, content_type='json')