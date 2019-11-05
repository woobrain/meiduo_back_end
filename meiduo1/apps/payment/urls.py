from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^payment/(?P<order_id>\d+)/', views.PayComView.as_view(),name='order_id'),
    url(r'^payment/status/', views.PayStatusView.as_view(),name='status'),


]