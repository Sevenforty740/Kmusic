# -*- coding: UTF-8 -*-
import logging
import urllib
import re
from rest_framework.response import Response
from rest_framework.views import APIView
from main.models import *
from django.middleware.csrf import get_token
from api.search4api import *
import requests
import base64
import execjs
from KMusic.settings import BASE_DIR
from api.search4api import MusicSearcher

# Create your views here.
class CsrfView(APIView):
    """
    获取Csrf_token \n
    :return: csrf_token
    """
    permission_classes = []

    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        res = {
            "error": 0,
            "msg": None,
            "data": {"csrf_token": csrf_token}
        }
        return Response(data=res)


class PasswordView(APIView):
    """
    修改密码 \n
    :Headers Authorization: JWT + ' ' + token \n
    :param old_password: 原密码string \n
    :param new_password: 新密码string \n
    :return: 成功或失败
    """
    def put(self, request, *args, **kwargs):
        res = {
            'error': 0,
            'msg': None
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

        return Response(data=res)


class SongListsView(APIView):
    """
    用户歌单列表概况 \n
    :Headers Authorization: JWT + ' ' + token \n
    :return: 该用户所有歌单概况
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

        return Response(data=res)


class SongListView(APIView):
    """
    增删改查单个歌单
    """

    def get(self, request, *args, **kwargs):
        """
        查询某个歌单详细内容 \n
        :Headers Authorization: JWT + ' ' + token \n
        :param list_id: 歌单id \n
        :return: 成功或失败
        """
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
            res['data']['songs'] = [{"song_id": song.songid,
                                     "source": song.source,
                                     "name": song.name,
                                     "artist": song.artist,
                                     "duration": song.duration
                                     } for song in songlist.song_set.all()]
            res['data']['list_name'] = songlist.listname

        except Exception as e:
            logging.error(e)
            res['error'] = 1
            res['msg'] = "未找到该歌单"

        return Response(data=res)

    def post(self, request, *args, **kwargs):
        """
        新建一个歌单 \n
        :Headers Authorization: JWT + ' ' + token \n
        :param list_name: 新建的歌单名称 \n
        :return: 成功或失败  歌单id：list_id  歌单名称list_name
        """
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
            return Response(data=res)
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
            return Response(data=res)

    def put(self, request, *args, **kwargs):
        """
        更改歌单名称 \n
        :Headers Authorization: JWT + ' ' + token \n
        :param list_name: 修改前的歌单名称 \n
        :param new_name:  修改后的歌单名称 \n
        :return: 成功或失败  歌单id：list_id  歌单名称list_name
        """
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
            return Response(data=res)

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
        return Response(data=res)

    def delete(self, request, *args, **kwargs):
        """
        删除歌单 \n
        :Headers Authorization: JWT + ' ' + token \n
        :param list_name: 要删除的歌单名称 \n
        :return: 成功或失败
        """
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
        return Response(data=res)


class SongView(APIView):
    """歌曲在歌单中的添加与删除"""

    def post(self, request, *args, **kwargs):
        """
        歌单中添加歌曲 \n
        :Headers Authorization: JWT + ' ' + token \n
        :param list_id: 歌单id \n
        :param song_id: 搜索接口返回的song_id \n
        :param source: 搜索接口返回的来源source \n
        :param song_name: 搜索接口返回的歌名name \n
        :param artist: 搜索接口返回的歌手artist \n
        :param duration: 搜索接口返回的时长duration \n
        :return: 成功或失败
        """
        user_id = request.user.id
        list_id = request.data.get('list_id')
        song_id = request.data.get('song_id')
        source = request.data.get('source')
        songname = request.data.get('song_name')
        artist = request.data.get('artist')
        artist = re.sub('&nbsp;', ' ', artist)
        duration = request.data.get('duration')
        songlist = Songlist.objects.filter(
            user_id=user_id, id=list_id, isdelete=False).first()
        isExists = Song.objects.filter(
            songid=song_id,
            source=source,
            name=songname,
            songlist_id=songlist.id).first()
        if isExists:
            res = {
                "error": 1,
                "msg": "该歌曲已经在歌单中",
                "data": None
            }
            return Response(data=res)
        else:
            Song.objects.create(
                songid=song_id,
                source=source,
                name=songname,
                artist=artist,
                duration=duration,
                songlist_id=songlist.id)
            res = {
                "error": 0,
                "msg": "添加成功",
                "data": None
            }
            return Response(data=res)

    def delete(self, request, *args, **kwargs):
        """
        歌单中删除歌曲 \n
        :Headers Authorization: JWT + ' ' + token \n
        :param list_id: 歌单id \n
        :param song_id: 搜索接口返回的song_id \n
        :param source: 搜索接口返回的来源source \n
        :return: 成功或失败
        """
        user_id = request.user.id
        list_id = request.data.get('list_id')
        song_id = request.data.get('song_id')
        source = request.data.get('source')
        songlist = Songlist.objects.filter(
            user_id=user_id, id=list_id, isdelete=False).first()
        if songlist:
            song = Song.objects.filter(
                songlist_id=list_id,
                songid=song_id,
                source=source).first()
            if song:
                song.delete()
                res = {
                    "error": 0,
                    "msg": "歌曲已删除",
                    "data": None
                }
            else:
                res = {
                    "error": 1,
                    "msg": "提供的信息有误",
                    "data": None
                }
        else:
            res = {
                "error": 1,
                "msg": "提供的信息有误",
                "data": None
            }
        return Response(data=res)


class SearchView(APIView):
    """
    搜索 \n
    :param keyword: 搜索关键字 \n
    :return: qq netease kuwo 三家详细搜索结果
    """
    permission_classes = []

    def get(self, request, *args, **kwargs):
        target = request.query_params.get('keyword')
        target = urllib.parse.unquote(target)
        searcher = MusicSearcher()
        res = searcher.search(target)
        del searcher
        return Response(data=res)


class Register(APIView):
    """
    注册用户 \n
    :param username: 用户名 \n
    :param password: 密码 \n
    :param email: 邮箱 可选填 \n
    :return: 成功或失败 userid，username
    """
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
            email = request.data.get('email', '')
            password = request.data.get('password')
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()
            res['msg'] = "注册成功"
            res['data'] = {
                "user_id": user.id,
                "user_name": user.username
            }
        return Response(data=res)


class RadioSearchView(APIView):
    """
    电台搜索接口 暂时只支持网易云 且只支持搜索播放 不能加入歌单 \n

    """
    permission_classes = []

    def get(self, request, *args, **kwargs):
        kw = request.query_params.get('kw')

        s = requests.session()
        s.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            # 'Cookie': '_xmLog=xm_1564455319501_jyp8ay8dfpas2z; x_xmly_traffic=utm_source%253A%2526utm_medium%253A%2526utm_campaign%253A%2526utm_content%253A%2526utm_term%253A%2526utm_from%253A; device_id=xm_1564455319822_jyp8ayha85acit; Hm_lvt_4a7d8ec50cfd6af753c4f8aee3425070=1564455320; Hm_lpvt_4a7d8ec50cfd6af753c4f8aee3425070=1564455320',
            'Host': 'www.ximalaya.com',
            'Referer': 'https://www.ximalaya.com/yule/15341221/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            # 'xm-sign': '2d8dd82ebf9dcfd304f6d9d196c94754(78)1564455349727(5)1564455350531',
        }

        params = {
            'core': 'all',
            'kw': kw,
            'spellchecker': 'true',
            'device': 'iPhone',
        }
        s.get("https://www.ximalaya.com")

        res = s.get("https://www.ximalaya.com/revision/search",
                    params=params)
        res = json.loads(res.text)

        albums = res['data']['result']['album']
        results = []
        for album in albums['docs']:
            r_album = {}
            try:
                r_album['cover_path'] = album['cover_path']
                r_album['title'] = album['title']
                r_album['url'] = album['url']
                r_album['id'] = album['id']
                r_album['is_paid'] = album['is_paid']
                r_album['tracks'] = album['tracks']
                r_album['id'] = album['id']
                r_album['pages'] = math.ceil(album['tracks'] / 30)
            except:
                pass
            results.append(r_album)

        res = {
            'error': 0,
            'msg':"success",
            'data': results
        }
        return Response(res)


class RadioDetailView(APIView):
    """
    单个电台栏目详细信息获取
    """
    permission_classes = []

    def getxmtime(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'Accept': 'text/html,application/xhtml+ xml,application/xml;q = 0.9,image/webp,image/apng,*/*;q=0.8, application/signe-exchange;v = b3',
            'Host': 'www.ximalaya.com'
        }
        url = "https://www.ximalaya.com/revision/time"
        response = requests.get(url, headers=headers)
        html = response.text
        return html

    def exec_js(self):
        time = self.getxmtime()
        path = BASE_DIR + "\\api\\radiojs\\xmSign.js"
        with open(path, encoding='utf-8') as f:
            js = f.read()

        docjs = execjs.compile(js)
        res = docjs.call('python', time)
        return res

    def get(self,request,*args,**kwargs):
        radio_id = request.query_params.get('id')
        page = request.query_params.get('page')

        s = requests.session()
        s.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            # 'Cookie': '_xmLog=xm_1564455319501_jyp8ay8dfpas2z; x_xmly_traffic=utm_source%253A%2526utm_medium%253A%2526utm_campaign%253A%2526utm_content%253A%2526utm_term%253A%2526utm_from%253A; device_id=xm_1564455319822_jyp8ayha85acit; Hm_lvt_4a7d8ec50cfd6af753c4f8aee3425070=1564455320; Hm_lpvt_4a7d8ec50cfd6af753c4f8aee3425070=1564455320',
            'Host': 'www.ximalaya.com',
            'Referer': 'https://www.ximalaya.com/yule/15341221/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            # 'xm-sign': '2d8dd82ebf9dcfd304f6d9d196c94754(78)1564455349727(5)1564455350531',
        }
        pageurl = "https://www.ximalaya.com/revision/play/album"
        params = {
            'albumId': radio_id,
            'pageNum': page,
            'sort': 1,
            'pageSize': 30,
        }

        xm_sign = self.exec_js()
        s.headers['xm-sign'] = xm_sign
        res2 = s.get(pageurl, params=params)
        res2 = json.loads(res2.text)
        song_list = res2['data']['tracksAudioPlay']

        res = {
            'error': 0,
            'msg':'success',
            'data':{
                'programs':song_list
            }
        }
        return Response(data=res)


class SongDetailView(APIView):
    permission_classes = []
    def post(self,request,*args,**kwargs):
        data = request.data.dict()
        source = data['source']
        songid = data['song_id']
        if source == 'netease':
            # 歌词
            lyric_url = 'http://music.163.com/api/song/lyric?os=osx&id={}&lv=-1&kv=-1&tv=-1'.format(
                songid)
            res = requests.get(lyric_url)
            res.encoding = 'utf-8'
            res = json.loads(res.text)
            lyric = res['lrc']['lyric']
            data['lyric'] = lyric
            # 播放url
            url = "http://music.163.com/song/media/outer/url?id={}.mp3".format(
                songid)
            data['url'] = url

        elif source == 'kuwo':
            # 歌词
            lyric_url = 'http://m.kuwo.cn/newh5/singles/songinfoandlrc?musicId={}'.format(
                songid)
            res = requests.get(lyric_url)
            res.encoding = "utf-8"
            res = json.loads(res.text)
            lyric = res['data']['lrclist']
            data['lyric'] = lyric

            def timeformat(time):
                time = float(time)
                minute = time // 60
                second = round(time - minute * 60, 3)
                return "[%02d:%06.3f]" % (minute, second)

            lyric_format = "\n".join(
                [timeformat(line['time']) + line['lineLyric'] for line in lyric])
            data['lyric'] = lyric_format
            # url
            url_params = {
                'format': 'mp3',
                'rid': songid,
                'response': 'url',
                'type': 'convert_url3',
                'br': '320kmp3',
                'from': 'web',
                't': str(int(time.time() * 1000)),
            }
            res = requests.get('http://www.kuwo.cn/url', params=url_params)
            res = json.loads(res.text)
            # {"code": 200, "msg": "success", "url": "https://nc01-sycdn.kuwo.cn/af8dcf1a5850a74edaf02433904bebc2/5d5a3e1e/resource/n3/36/12/1210429732.mp3"}
            data['url'] = res['url']

        elif source == 'qq':
            # 歌词
            headers = {
                'Connection': 'Keep-Alive',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN',
                'Accept': '*/*',
                'User-Agent': 'Mozilla/5.0(compatible;MSIE 9.0;Windows NT 6.1;WOW64;Trident/5.0)',
                'Host': 'c.y.qq.com',
                'Referer': 'c.y.qq.com',
            }

            lyric_url1 = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg'
            params = {
                '-': 'MusicJsonCallback_lrc',
                'pcachetime': str(int(time.time() * 1000)),
                'songmid': songid,
                'g_tk': '5381',
                'loginUin': '0',
                'hostUin': '0',
                'format': 'json',
                'inCharset': 'utf8',
                'outCharset': 'utf - 8',
                'notice': '0',
                'platform': 'yqq.json',
                'needNewCode': '0',
            }
            res1 = requests.get(lyric_url1, params=params, headers=headers)
            res1 = json.loads(res1.text)
            lyric = base64.b64decode(res1['lyric']).decode()
            data['lyric'] = lyric

            # url
            vkey_url = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg'
            data_qq = {
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
                'songmid': songid,
                'filename': 'C400{}.m4a'.format(songid),
                'guid': 'B1E901DA7379A44022C5AF79FDD9CD96'
            }
            res = requests.get(vkey_url, params=data_qq, verify=False)
            res = json.loads(res.text[36:-1])
            vkey = res['data']['items'][0]['vkey']
            url = 'http://111.202.85.147/amobile.music.tc.qq.com/C400{}.m4a?guid=B1E901DA7379A44022C5AF79FDD9CD96&vkey={}&uin=2521&fromtag=77'.format(
                songid, vkey)
            data['url'] = url

        elif source == 'xiami':
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                'referer': 'http://m.xiami.com/'
            }
            # 歌词
            try:
                lyric_file = data['lyric']
                lyric_res = requests.get(lyric_file,headers=headers)
                lyric_res.encoding = "utf-8"
                lyric_before = lyric_res.text
                lyric = re.sub(r'<\d+?>','',lyric_before,flags=re.S)
            except KeyError:
                lyric = ''
            data['lyric'] = lyric

            # url
            url = 'http://api.xiami.com/web'
            params = {
                "v": "2.0",
                "app_key": "1",
                "r": "song/detail",
                "id": songid,
            }
            res = requests.get(url, params=params, headers=headers)
            res.encoding = "utf-8"
            res = json.loads(res.text)
            url = res['data']['song'].get('listen_file','')
            data['url'] = url

        result = {
            'error':0,
            'data':data
        }
        return Response(data=result)