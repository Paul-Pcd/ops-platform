from django.conf.urls import url
from . import views
from resources.server import AutoReportingView, ServerListView

urlpatterns = [
    url(r'^index$', views.index_view),
    url(r'server/reporting/$', AutoReportingView.as_view()),
    url(r'server/list/$', ServerListView.as_view()),
]

