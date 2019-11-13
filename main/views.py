import json,re
import time
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
    if request.COOKIES.get('user_id') and request.COOKIES.get('user_name'):
        request.session['user_id'] = request.COOKIES['user_id']
        request.session['user_name'] = request.COOKIES['user_name']
    return render(request,'index.html')


def search_views(request):
    target = request.GET.get('s')
    target = urllib.parse.unquote(target)
    searcher = MusicSearcher(target,q)
    threadQQ =Thread(target=searcher.qqSearch)
    threadnetE = Thread(target=searcher.netEaseSearch)
    threadkuWo = Thread(target=searcher.kuWoSearch)
    threadQQ.start()
    threadnetE.start()
    threadkuWo.start()
    threadQQ.join()
    threadnetE.join()
    threadkuWo.join()
    first = q.get()
    second = q.get()
    third = q.get()

    params = {
        'target':target,
        first[0]: first,
        second[0]:second,
        third[0]:third
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
    songlists = Songlist.objects.filter(user_id=user_id).all()
    list_name = request.GET.get('listname')
    list = Songlist.objects.filter(user_id=user_id,listname=list_name).first()
    songs = Song.objects.filter(songlist_id=list.id).all()

    return render(request,'songlist.html',locals())


def addSong_views(request):
    if request.method == 'GET':
        if request.session.get('user_id'):
            user_id = request.session['user_id']
            songlists = Songlist.objects.filter(user_id=user_id).all()
            songlists_l = [songlist.listname for songlist in songlists]
            songlists_l = json.dumps(songlists_l)
            return HttpResponse(songlists_l)
        else:
            return HttpResponse('请您先登录账号 才可使用歌单功能')
    else:
        user_id = request.session['user_id']
        songlist_name = request.POST.get('songlist_name')
        song_id = request.POST.get('songid')
        source = request.POST.get('source')
        songname = request.POST.get('songname')
        artist = request.POST.get('artist')
        artist = re.sub('&nbsp;', ' ', artist)
        artist = re.sub('&amp;', '&', artist)
        duration = request.POST.get('duration')
        songlist = Songlist.objects.filter(user_id=user_id,listname=songlist_name).first()
        isExists = Song.objects.filter(songid=song_id, source=source,name=songname,songlist_id=songlist.id).first()
        if isExists:
            return HttpResponse('exists')
        else:
            Song.objects.create(songid=song_id, source=source,name=songname,artist=artist,duration=duration,songlist_id=songlist.id)
            return HttpResponse('ok')


def listRmSong_views(request):
    user_id = request.session['user_id']
    songlist_name = request.GET.get('listname')
    name = request.GET.get('name')
    duration = request.GET.get('duration')
    source = request.GET.get('source')
    artist = request.GET.get('artist')
    artist = re.sub('&amp;', '&', artist)
    songlist = Songlist.objects.filter(user_id=user_id,listname=songlist_name).first()
    song = Song.objects.filter(songlist_id=songlist.id,name=name, source=source,duration=duration,artist=artist).first()
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


def getSongUrl_views(request):
    if request.method == 'POST':
        songid = request.POST.get('songid')
        source = request.POST.get('source')

        if source == 'netease':
            url = "http://music.163.com/song/media/outer/url?id={}.mp3".format(songid)

        elif source == 'qq':
            data = {
                "req": {"module": "CDN.SrfCdnDispatchServer", "method": "GetCdnDispatch",
                        "param": {"guid": "1848955700", "calltype": 0, "userip": ""}},
                "req_0": {"module": "vkey.GetVkeyServer",
                          "method": "CgiGetVkey",
                          "param": {"guid": "1848955700", "songmid": [songid], "songtype": [0], "uin": "125045209",
                                    "loginflag": 1, "platform": "20"}},
                "comm": {"uin": 125045209, "format": "json", "ct": 24, "cv": 0}
            }
            data = urllib.parse.quote(json.dumps(data))
            vkey_url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?-=getplaysongvkey14973006206196215&g_tk=5381&loginUin=125045209&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&data={}'.format(
                data)
            res = requests.get(vkey_url)
            res = json.loads(res.text)
            url = r"{}{}".format(res['req_0']['data']['sip'][0],res['req_0']['data']['midurlinfo'][0]['purl'])
            

        elif source == 'kuwo':
            url_params = {
                'format': 'mp3',
                'rid': songid,
                'response': 'url',
                'type': 'convert_url3',
                'br': '256kmp3',
                'from': 'web',
                't': str(int(time.time() * 1000)),
                'reqId': '3cb750f1-a387-11e9-bf69-fbb42f0bf2bb'
            }
            res = requests.get('http://www.kuwo.cn/url', params=url_params)
            res = json.loads(res.text)
            url = res['url']
        else:
            url = 'error'

        return HttpResponse(url)





