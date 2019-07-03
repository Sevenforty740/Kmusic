from django.urls import path,re_path
from .views import *
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # re_path(r'^$',index_views),
    # re_path(r'^search/$',search_views),
    # re_path(r'^songlist/$', songList_views),
    # re_path(r'^addsong/$',addSong_views),
    # re_path(r'^qplysong/$',qPlaySong_views),
    # re_path(r'^chgsonglist/$', chgSongList_views),
    # re_path(r'^listrmsong/$',listRmSong_views),
    # re_path(r'^rmlist/$', removeList_views),
    re_path(r'^csrf_token/$',CsrfView.as_view()),
    re_path(r'^auth/$', obtain_jwt_token),
    re_path(r'^songlists/$', SongListsView.as_view()),
    re_path(r'^songlist/$', SongListView.as_view()),
    re_path(r'^register/$', Register.as_view()),
    re_path(r'^qqsong/$', QPlaysong.as_view()),
    re_path(r'^search/$', SearchView.as_view()),
    re_path(r'^song/$', SongView.as_view()),
    re_path(r'^password/$', PasswordView.as_view()),
    # re_path(r'^songlist/$', AuthView.as_view()),
]