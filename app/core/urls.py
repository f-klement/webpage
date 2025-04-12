# main/urls.py

#from crowdsec_views.views import ban_view
from django.urls import path
from . import views


urlpatterns = [
    path('ban/', views.ban_view, name='ban_view'),
    #path('ban/', view=ban_view, name='ban_view'),
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('services/nextcloud/', views.nextcloud, name='nextcloud'),
    path('ghostblog/', views.GhostLog, name='GhostLog'),
    path('services/jellyfin/', views.jellyfin, name='jellyfin'),
    path('blog/', views.blog, name='blog'),
    path('favicon.ico', views.favicon, name='favicon'),
]
