from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    url('checkout/', views.checkout, name='checkout'),
    url('confirm/', views.confirm, name='confirm'),
]
