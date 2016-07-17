from django.conf.urls import url
from . import views
from resources.server import *
from resources.server.status import *
from resources.product import *

urlpatterns = [
    url(r'^index$', views.index_view),
    url(r'server/reporting/$', AutoReportingView.as_view()),
    url(r'server/list/$', ServerListView.as_view()),
    url(r'server/status/add/$', StatusAddView.as_view()),
    url(r'server/modify/status/$', ServerModifyStatusView.as_view()),
    url(r'server/modify/product/$', ServerModifyProductView.as_view()),
    url(r'product/add/$', ProductAddView.as_view()),
    url(r'product/get/$', ProductJsonResponse.as_view()),
]

