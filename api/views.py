from threading import Thread
import logging,urllib,re
from queue import Queue
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from main.models import *
from django.middleware.csrf import get_token
from main.apis.musicsearcher import *
from rest_framework import exceptions

class APIMusicSearcher(MusicSearcher):
    def netEaseSearch(self):
        self.headers['Host'] = 'music.163.com'
        self.headers['Referer'] = 'http://music.163.com/'

        data = {
            's': self.target,
            'offset': '0',
            'limit': '100',
            'type': '1'
        }

        url = 'https://music.163.com/weapi/cloudsearch/get/web'
        # 获得params encSecKey两个加密参数
        data = encrypted_request(data)
        response = self.s.post(url, data=data, headers=self.headers)
        r_d = json.loads(response.text)
        r_l = r_d['result']['songs']

        resultList = ['netease']
        for song in r_l:
            songDic = {}
            songDic['songname'] = song['name']
            id = song['id']
            songDic['songid'] = id
            songDic['tottime'] = getNeTime(song['dt'])
            songDic['singerid'] = song['ar'][0]['id']
            songDic['singername'] = song['ar'][0]['name']
            songDic['albumid'] = song['al']['id']
            songDic['albumname'] = song['al']['name']
            songDic['albumpic'] = song['al']['picUrl']
            songDic['playurl'] = "http://music.163.com/song/media/outer/url?id={}.mp3".format(id)
            resultList.append(songDic)

        self.q.put(resultList)

# Create your views here.

class CsrfView(APIView):
    """
    获取Csrf_token
    """
    permission_classes = []

    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        res = {
            "error": 0,
            "msg": None,
            "data": {"csrf_token": csrf_token}
        }
        return JsonResponse(res)


class PasswordView(APIView):
    """修改密码"""
    def put(self,request,*args,**kwargs):
        res = {
            'error':0,
            'msg':None
        }

        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if user.check_password(old_password):
            if old_password == new_password:
                res['error'] = 1
                res['msg'] = '新密码与旧密码相同'
            else:
                user.set_password(new_password)
                user.save()
                res['msg'] = '密码修改成功'
        else:
            res['error'] = 1
            res['msg'] = '输入的原密码有误'

        return JsonResponse(res)


class SongListsView(APIView):
    """
    用户歌单列表概况
    """

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        songlists = Songlist.objects.filter(
            user_id=user_id, isdelete=False).all()
        res = {
            "error": 0,
            "msg": None,
            "data": {
                "user_id": user_id,
                "user_name": request.user.username,
                "list_count": len(songlists),
                "songlists": []
            }
        }
        if songlists:
            res['data']['songlists'] = [
                {
                    "list_id": songlist.id,
                    "name": songlist.listname,
                    "count": songlist.song_set.count()} for songlist in songlists]

        return JsonResponse(res)


class SongListView(APIView):
    """
    增删改查单个歌单
    """
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """查询某个歌单详细内容"""
        user_id = request.user.id
        list_id = request.query_params.get('list_id')

        res = {
            "error": 0,
            "msg": None,
            "data": {
                "user_id": request.user.id,
                "user_name": request.user.username,
                "list_name": "",
                "songs": []
            }
        }

        try:
            songlist = Songlist.objects.get(
                id=list_id, user_id=user_id, isdelete=False)
            res['data']['songs'] = [{"id": song.id,
                                     "name": song.name,
                                     "singer": song.singer,
                                     "duration": song.duration,
                                     "url": song.url} for song in songlist.song_set.all()]
            res['data']['list_name'] = songlist.listname

        except Exception as e:
            logging.error(e)
            res['error'] = 1
            res['msg'] = "未找到该歌单"

        return Response(data=res)

    def post(self, request, *args, **kwargs):
        """新建一个歌单"""
        res = {
            "error": 0,
            "msg": "",
            "data": {}
        }
        user_id = request.user.id
        list_name = request.data.get('list_name')
        songlist = Songlist.objects.filter(
            user_id=user_id,
            listname=list_name,
            isdelete=False).first()
        if songlist:
            res["error"] = 1
            res["msg"] = "该歌单名已经存在"
            return JsonResponse(res)
        else:
            songlist = Songlist.objects.filter(
                user_id=user_id,
                listname=list_name,
                isdelete=True).first()
            if songlist:
                songs = Song.objects.filter(songlist=songlist.id).all()
                songs.delete()
                songlist.isdelete = False
                songlist.save()
            else:
                songlist = Songlist.objects.create(
                    listname=list_name, user_id=user_id)
            res["msg"] = "歌单创建成功"
            res["data"] = {
                "list_id": songlist.id,
                "list_name": songlist.listname,
            }
            return JsonResponse(res)

    def put(self, request, *args, **kwargs):
        """更改歌单名称"""
        res = {
            "error": 0,
            "msg": "",
            "data": {}
        }
        user_id = request.user.id
        list_name = request.data.get('list_name')
        new_name = request.data.get('new_name')
        try:
            songlist = Songlist.objects.get(
                user_id=user_id, listname=list_name, isdelete=False)
        except Exception as e:
            res['error'] = 1
            res['msg'] = "未找到歌单"
            return JsonResponse(res)

        try:
            elist = Songlist.objects.get(
                user_id=user_id, listname=new_name, isdelete=True)
            elist.delete()
        except Exception as e:
            pass

        songlist.listname = new_name
        songlist.save()

        res['msg'] = "歌单名称修改完成"
        res['data'] = {
            "list_id": songlist.id,
            "list_name": songlist.listname
        }
        return JsonResponse(res)

    def delete(self, request, *args, **kwargs):
        """删除歌单"""
        user_id = request.user.id
        list_name = request.data.get('list_name')
        try:
            songlist = Songlist.objects.get(
                user_id=user_id, listname=list_name, isdelete=False)
            songlist.isdelete = True
            songlist.save()
            res = {
                "error": 0,
                "msg": "歌单删除成功",
                "data": {}
            }
        except Exception as e:
            logging.error(e)
            res = {
                "error": 1,
                "msg": "未找到该歌单",
                "data": {}
            }
        return JsonResponse(res)


class SongView(APIView):
    """歌曲在歌单中的添加与删除"""

    def post(self,request,*args,**kwargs):
        """歌单中添加歌曲"""
        user_id = request.user.id
        listname = request.data.get('listname')
        songurl = request.data.get('songurl')
        songurl = re.sub('&amp;', '&', songurl)
        songname = request.data.get('songname')
        singer = request.data.get('singer')
        singer = re.sub('&nbsp;', ' ', singer)
        duration = request.data.get('duration')
        songlist = Songlist.objects.filter(user_id=user_id, listname=listname,isdelete=False).first()
        isExists = Song.objects.filter(url=songurl, name=songname, songlist_id=songlist.id).first()
        if isExists:
            res = {
                "error":1,
                "msg":"该歌曲已经在歌单中",
                "data":None
            }
            return JsonResponse(res)
        else:
            Song.objects.create(url=songurl, name=songname, singer=singer, duration=duration, songlist_id=songlist.id)
            res = {
                "error": 0,
                "msg": "添加成功",
                "data": None
            }
            return JsonResponse(res)

    def delete(self,request,*args,**kwargs):
        user_id = request.user.id
        listname = request.data.get('listname')
        songname = request.data.get('songname')
        duration = request.data.get('duration')
        songlist = Songlist.objects.filter(user_id=user_id, listname=listname,isdelete=False).first()
        song = Song.objects.filter(songlist_id=songlist.id, name=songname, duration=duration).first()
        song.delete()
        res = {
            "error":0,
            "msg":"歌曲已删除",
            "data":None
        }
        return JsonResponse(res)


class SearchView(APIView):
    """搜索"""
    permission_classes = []
    def get(self,request,*args,**kwargs):
        q = Queue()
        target = urllib.parse.unquote(request.query_params.get('keyword'))
        searcher = APIMusicSearcher(target, q)
        threadQQ = Thread(target=searcher.qqSearch)
        threadnetE = Thread(target=searcher.netEaseSearch)
        threadQQ.start()
        threadnetE.start()
        threadQQ.join()
        threadnetE.join()
        first = q.get()
        if first[0] == 'qq':
            res = {
                'error':0,
                'msg':None,
                'data':{
                    'target': target,
                    'qqRes': first[1:],
                    'netEaseRes': q.get()[1:]
                }
            }
        else:
            res = {
                'error': 0,
                'msg': None,
                'data': {
                    'target': target,
                    'netEaseRes': first[1:],
                    'qqRes': q.get()[1:]
                }
            }
        return Response(data=res)


class QPlaysong(APIView):
    """QQ的歌曲获得最终的完整url"""
    permission_classes = []

    def post(self, request, *args, **kwargs):
        mid = request.data.get('mid')
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
        qres = requests.get(vkey_url, params=data, verify=False)
        qres = json.loads(qres.text[36:-1])
        vkey = qres['data']['items'][0]['vkey']
        url = 'http://111.202.85.147/amobile.music.tc.qq.com/C400{}.m4a?guid=B1E901DA7379A44022C5AF79FDD9CD96&vkey={}&uin=2521&fromtag=77'.format(
            mid, vkey)

        res = {
            "error" : 0,
            "msg":None,
            "data":{
                "url":url,
            }
        }
        return JsonResponse(res)


class Register(APIView):
    """注册用户"""
    permission_classes = []

    def post(self, request, *args, **kwargs):
        res = {
            "error": 0,
            "msg": "",
            "data": {}
        }
        username = request.data.get('username')
        user = User.objects.filter(username=username).first()
        if user:
            res['error'] = 1
            res['msg'] = "该用户名已被占用"
        else:
            email = request.data.get('email')
            password = request.data.get('password')
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()
            res['msg'] = "注册成功"
            res['data'] = {
                "user_id": user.id,
                "user_name": user.username
            }
        return JsonResponse(res)

