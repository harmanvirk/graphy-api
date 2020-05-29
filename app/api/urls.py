from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^fetch_all/', views.index, name='fetch_all'),
    url(r'^create/?', views.create, name='create'),
    url(r'^fetch_media/(?P<story_id>\d+)/$', views.fetch_media, name='fetch_media'),
]
