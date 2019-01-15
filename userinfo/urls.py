from django.urls import path,re_path
from .views import *

urlpatterns = [
    re_path('^register/',register_views),
    re_path('^logout/',logout_views),
    re_path('^login/',login_views),
]