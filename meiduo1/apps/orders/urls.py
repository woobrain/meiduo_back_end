from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^orders/commit/$', views.OrderComView.as_view(),name='commit'),
    url(r'^orders/success/', views.OrderSucView.as_view(), name='success'),

]