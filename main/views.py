import json,re
import urllib
from django.http import HttpResponse
from django.shortcuts import render, redirect
from queue import Queue
from threading import Thread
from .apis.musicsearcher import MusicSearcher
from .models import *
import requests


q = Queue()  # 用于接收Thread线程的返回值


# Create your views here.
def index_views(request):
    if request.session.get('user_id') and request.session.get('user_name'):
        return render(request,'index.html')
    else:
        if request.COOKIES.get('user_id') and request.COOKIES.get('user_name'):
            request.session['user_id'] = request.COOKIES['user_id']
            request.session['user_name'] = request.COOKIES['user_name']
        return  render(request,'index.html')



def search_views(request):
    target = request.GET.get('s')
    target = urllib.parse.unquote(target)
    searcher = MusicSearcher(target,q)
    threadQQ =Thread(target=searcher.qqSearch)
    threadnetE = Thread(target=searcher.netEaseSearch)
    threadQQ.start()
    threadnetE.start()
    threadQQ.join()
    threadnetE.join()
    first = q.get()
    if first[0] == 'qq':
        params = {
            'target':target,
            'qqRes': first,
            'netEaseRes':q.get()
        }
    else:
        params = {
            'target': target,
            'netEaseRes':first,
            'qqRes':q.get()
        }
    return render(request, 'srchresult.html', params)


def songList_views(request):
    user_id = request.session.get('user_id')
    songlists = Songlist.objects.filter(user_id=user_id).all()
    if songlists:
        list = songlists[0]
        songs = Song.objects.filter(songlist_id=list.id).all()

    return render(request,'songlist.html',locals())


def chgSongList_views(request):
    user_id = request.session.get('user_id')
    list_name = request.GET.get('listname')
    songlists = Songlist.objects.filter(user_id=user_id).all()
    list = Songlist.objects.filter(user_id=user_id,listname=list_name).first()
    songs = Song.objects.filter(songlist_id=list.id).all()

    return render(request,'songlist.html',locals())


def addSong_views(request):
    if request.method == 'GET':
        if request.session.get('user_id'):
            user_id = request.session['user_id']
            songlists = Songlist.objects.filter(user_id=user_id).all()
            songlists_l = []
            for songlist in songlists:
                songlists_l.append(songlist.listname)
            songlists_l = json.dumps(songlists_l)
            return HttpResponse(songlists_l)
        else:
            return HttpResponse('请您先登录账号 才可使用歌单功能')
    else:
        user_id = request.session['user_id']
        songlist_name = request.POST.get('songlist_name')
        songurl = request.POST.get('songurl')
        songurl = re.sub('&amp;','&',songurl)
        songname = request.POST.get('songname')
        singer = request.POST.get('singer')
        singer = re.sub('&nbsp;', ' ', singer)
        duration = request.POST.get('duration')
        songlist = Songlist.objects.filter(user_id=user_id,listname=songlist_name).first()
        isExists = Song.objects.filter(url=songurl,name=songname,songlist_id=songlist.id).first()
        if isExists:
            return HttpResponse('exists')
        else:
            Song.objects.create(url=songurl,name=songname,singer=singer,duration=duration,songlist_id=songlist.id)
            return HttpResponse('ok')


def listRmSong_views(request):
    user_id = request.session['user_id']
    songlist_name = request.GET.get('listname')
    songname = request.GET.get('songname')
    duration = request.GET.get('duration')
    songlist = Songlist.objects.filter(user_id=user_id,listname=songlist_name).first()
    song = Song.objects.filter(songlist_id=songlist.id,name=songname,duration=duration).first()
    song.delete()
    return HttpResponse('remove song ok')


def removeList_views(request):
    user_id = request.session['user_id']
    songlist_name = request.GET.get('listname')
    tsonglist = Songlist.objects.filter(user_id=user_id,listname=songlist_name).all()
    tsonglist.delete()
    return redirect('/songlist/')


def createList_views(request):
    if request.method == 'GET':
        user_id = request.session['user_id']
        list_name = request.GET.get('songlist_name')
        list = Songlist.objects.filter(user_id=user_id,listname=list_name).first()
        if list:
            return HttpResponse('该歌单名已经存在')
        else:
            return HttpResponse('&#12288;')

    else:
        user_id = request.session['user_id']
        list_name = request.POST.get('songlist_name')
        Songlist.objects.create(listname=list_name,user_id=user_id)

        return redirect('/songlist/')



def qPlaySong_views(request):
    if request.method == 'POST':
        mid = request.POST.get('mid')
        vkey_url = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg'
        data = {
            'g_tk': '195219765',
            'jsonpCallback': 'MusicJsonCallback004680169373158849',
            'loginUin': '125045209',
            'hostUin': '0',
            'format': 'json',
            'inCharset': 'utf8',
            'outCharset': 'utf-8',
            'notice': '0',
            'platform': 'yqq',
            'needNewCode': '0',
            'cid': '205361747',
            'callback': 'MusicJsonCallback004680169373158849',
            'uin': '125045209',
            'songmid': mid,
            'filename': 'C400{}.m4a'.format(mid),
            'guid': 'B1E901DA7379A44022C5AF79FDD9CD96'
        }
        res = requests.get(vkey_url, data, verify=False)
        res = json.loads(res.text[36:-1])
        vkey = res['data']['items'][0]['vkey']
        url = 'http://111.202.85.147/amobile.music.tc.qq.com/C400{}.m4a?guid=B1E901DA7379A44022C5AF79FDD9CD96&vkey={}&uin=2521&fromtag=77'.format(mid,vkey)
        return HttpResponse(url)





