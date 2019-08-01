from django.urls import path,re_path
from .views import *
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.documentation import include_docs_urls
API_TITLE = 'KMusic api documentation'


urlpatterns = [
    re_path(r'^csrf_token/$',CsrfView.as_view()),
    re_path(r'^auth/$', obtain_jwt_token),
    re_path(r'^songlists/$', SongListsView.as_view()),
    re_path(r'^songlist/$', SongListView.as_view()),
    re_path(r'^register/$', Register.as_view()),
    re_path(r'^geturl/$', GetUrl.as_view()),
    re_path(r'^search/$', SearchView.as_view()),
    re_path(r'^song/$', SongView.as_view()),
    re_path(r'^password/$', PasswordView.as_view()),
    re_path(r'^lyric/$',GetLyric.as_view()),
    re_path(r'^qqalbumpic/$', QQAlbumPic.as_view()),
    re_path(r'^radios/$',RadioSearchView.as_view()),
    re_path(r'^radio/$',RadioDetailView.as_view()),
    re_path(r'^docs/', include_docs_urls(title=API_TITLE, authentication_classes=[], permission_classes=[]))
]