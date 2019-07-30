#!/usr/bin/env python3
from django.urls import path,re_path
from .views import *

urlpatterns = [
    re_path(r'^$',index_views),
    re_path(r'^search/$',search_views),
    re_path(r'^songlist/$', songList_views),
    re_path(r'^addsong/$',addSong_views),
    re_path(r'^geturl/$',getSongUrl_views),
    re_path(r'^chgsonglist/$', chgSongList_views),
    re_path(r'^listrmsong/$',listRmSong_views),
    re_path(r'^rmlist/$', removeList_views),
    re_path(r'^createlist/$', createList_views),
]