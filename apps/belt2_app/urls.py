from django.conf.urls import url
##from django.contrib import admin
from . import views

urlpatterns = [
  url(r'^$', views.main, name='index'),
  url(r'^travels$', views.success, name='success'),
  url(r'^travels/destination/(?P<id>\d+)$', views.show, name='show'),
  url(r'^travels/add$', views.add_page, name='add_page'),  
  url(r'^create/$', views.create, name='create'),
  url(r'^join/(?P<id>\d+)$', views.join, name='join'),
  url(r'^register$', views.register, name='register'),
  url(r'^login$', views.login, name='login'),
  url(r'^logout$', views.logout, name='logout'),
]