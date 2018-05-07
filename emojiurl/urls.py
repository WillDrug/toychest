from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^/?$', views.emoji_index, name='emoji_index'),
    url(r'help/?', views.see_help, name='emoji_help'),
    url(r'make/?', views.make_link, name='show_link'),
    url(r'p/(?P<emojis>.*)/?', views.permanent_link, name='plink'),
    url(r'(?P<emojis>.*)/?', views.temp_link, name='tlink'),
]