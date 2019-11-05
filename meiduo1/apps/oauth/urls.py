from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^oauth_callback', views.QLoginView.as_view(),name='qq'),
    url(r'^qq/login/', views.QloginUrl.as_view(),name='qqlogin'),
    url(r'^weibo_callback', views.WLoginView.as_view(),name='weibo'),
    url(r'^weibo/login/', views.WloginUrl.as_view(),name='weibologin'),


]