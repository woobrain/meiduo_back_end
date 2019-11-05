from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^carts/$',views.CartsAddView.as_view(),name='addcart'),
    url(r'^carts/selection/$',views.CartsSelectedView.as_view(),name='selectcart'),
    url(r'^carts/simple/$', views.CartSimpleView.as_view(), name='simple'),

]