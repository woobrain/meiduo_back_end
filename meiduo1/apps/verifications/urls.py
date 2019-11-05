from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageView.as_view(),name='uuid'),
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.CodeView.as_view(),name='code'),


]