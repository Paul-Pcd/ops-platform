from django.conf.urls import url
from . import views
from resources.server import *
from resources.server.status import *

urlpatterns = [
    url(r'^index$', views.index_view),
    url(r'server/reporting/$', AutoReportingView.as_view()),
    url(r'server/list/$', ServerListView.as_view()),
    url(r'server/status/add/$', StatusAddView.as_view()),
    url(r'server/modify/status/$', ServerModifyStatusView.as_view()),
]

