# -*- coding: UTF-8 -*-
import requests
from threading import Thread
from .netEaseEncode import *
import time
import math
import queue


def getQQTime(s):
    s = s
    mi = s // 60
    se = s % 60
    return '%02d:%02d' % (mi, se)

def getNeTime(ms):
    s = ms / 1000
    mi = s // 60
    se = s % 60
    return '%02d:%02d' % (mi, se)

class MusicSearcher():
    def encrypted_params(self, keyword):
        _q = dict(key=keyword, pagingVO=dict(page=1, pageSize=60))
        _q = json.dumps(_q)
        url = "https://www.xiami.com/search?key={}".format(keyword)
        res = self.s.get(url)
        cookie = res.cookies.get("xm_sg_tk", "").split("_")[0]
        origin_str = "%s_xmMain_/api/search/searchSongs_%s" % (cookie, _q)
        _s = hashlib.md5(origin_str.encode()).hexdigest()
        return dict(_q=_q, _s=_s)

    def searchQQ(self, target, q):
        url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'

        headers = {
            'Accept': '*/*',
            'Connection': 'Keep-Alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'User-Agent': 'Mozilla/5.0(compatible;MSIE 9.0;Windows NT 6.1;WOW64;Trident/5.0)',
            'Host': 'c.y.qq.com',
            'Referer': 'c.y.qq.com'
        }

        params = {
            'format': 'json',
            't': 0,
            'loginUin': 0,
            'inCharset': 'GB2312',
            'outCharset': 'utf-8',
            'qqmusic_ver': 1653,
            'catZhida': 1,
            'p': 1,
            'n': 60,
            'w': target,
            'flag_qc': 0,
            'remoteplace': 'txt.newclient.top',
            'new_json': 1,
            'auto': 1,
            'lossless': 0,
            'aggr': 1,
            'cr': 1,
            'sem': 0,
            'force_zonghe': 0,
            'pcachetime': int(time.time()),
        }

        res = requests.get(url, params=params, headers=headers)
        search_res_dict = json.loads(res.text)
        result_dict = {
            "source": 'qq',
            "paginate": {
                "page": int(search_res_dict['data']['song']['curpage']),
                "pagesize": int(params['n']),
                "pages": int(math.ceil(int(search_res_dict['data']['song']['totalnum']) / int(params['n']))),
                "count": int(search_res_dict['data']['song']['totalnum'])
            },
            "songs": []
        }
        r_l = search_res_dict['data']['song']['list']
        for song in r_l:
            songDic = {}
            songDic['source'] = 'qq'
            songDic['name'] = song['name']
            songDic['song_id'] = song['mid']
            songDic['duration'] = getQQTime(song['interval'])
            songDic['artist_id'] = song['singer'][0]['id']
            songDic['artist'] = song['singer'][0]['name']
            songDic['album_id'] = song['album']['id']
            mid = song['album']['mid']
            songDic['album_pic'] = 'https://y.gtimg.cn/music/photo_new/T002R300x300M000{}.jpg'.format(
                mid)
            songDic['album'] = song['album']['name']
            result_dict['songs'].append(songDic)

        q.put_nowait(result_dict)

    def searchNetease(self, target, q):
        url = 'https://music.163.com/weapi/cloudsearch/get/web'

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'Keep-Alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/'
        }

        data_ne_b = {
            's': target,
            'offset': 0,
            'limit': 60,
            'type': 1
        }
        if data_ne_b['offset'] < 60:
            page = 1
        else:
            page = int(data_ne_b['offset'] / 60)

        data_ne = encrypted_request(data_ne_b)
        res = requests.post(url, headers=headers, data=data_ne)
        search_res_dict = json.loads(res.text)
        result_dict = {
            "source": 'netease',
            "paginate": {
                "page": page,
                "pagesize": data_ne_b['limit'],
                "pages": int(math.ceil(int(search_res_dict['result']['songCount']) / data_ne_b['limit'])),
                "count": search_res_dict['result']['songCount']
            },
            "songs": []
        }
        r_l = search_res_dict['result']['songs']
        for song in r_l:
            songDic = {}
            songDic['source'] = 'netease'
            songDic['name'] = song['name']
            songDic['song_id'] = song['id']
            songDic['duration'] = getNeTime(song['dt'])
            songDic['artist_id'] = song['ar'][0]['id']
            songDic['artist'] = song['ar'][0]['name']
            songDic['album_id'] = song['al']['id']
            songDic['album'] = song['al']['name']
            songDic['album_pic'] = song['al']['picUrl']
            result_dict['songs'].append(songDic)

        q.put_nowait(result_dict)

    def searchKuwo(self, target, q):
        url = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord'

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'Keep-Alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        }

        params = {
            'key': target,
            'pn': '1',
            'rn': '60',
        }

        res = requests.get(url, headers=headers, params=params)
        search_res_dict = json.loads(res.text)
        result_dict = {
            "source": 'kuwo',
            "paginate": {
                "page": int(params['pn']),
                "pagesize": int(params['rn']),
                "pages": int(math.ceil(int(search_res_dict['data']['total']) / int(params['rn']))),
                "count": int(search_res_dict['data']['total'])
            },
            "songs": []
        }

        for song in search_res_dict['data']['list']:
            d = {}
            d['source'] = 'kuwo'
            d['name'] = song['name']
            d['song_id'] = song['rid']
            d['artist'] = song['artist']
            d['artist_id'] = song['artistid']
            d['album'] = song['album']
            d['album_id'] = song['albumid']
            d['needPayFlag'] = 1 if song['isListenFee'] else 0
            try:
                d['album_pic'] = song['albumpic']
            except BaseException:
                pass
            d['duration'] = song['songTimeMinutes']
            result_dict['songs'].append(d)
        q.put_nowait(result_dict)

    def searchXiami(self, target, q):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'referer': 'http://m.xiami.com/'
        }
        search_url = 'http://api.xiami.com/web'
        params = {
            "key": target,
            "v": "2.0",
            "app_key": "1",
            "r": "search/songs",
            "page": 1,
            "limit": 50,
        }
        res = requests.get(search_url, params=params, headers=headers)
        res.encoding = "utf-8"
        search_res_dict = json.loads(res.text)

        result_dict = {
            "source": 'xiami',
            "paginate": {
                "page": int(params['page']),
                "pagesize": int(params['limit']),
                "pages": int(math.ceil(int(search_res_dict['data']['total']) / int(params['limit']))),
                "count": int(search_res_dict['data']['total'])
            },
            "songs": []
        }
        for song in search_res_dict["data"]["songs"]:
            r_dict = {}
            r_dict['source'] = 'xiami'
            r_dict['name'] = song['song_name']
            r_dict['song_id'] = song['song_id']
            try:
                r_dict['duration'] = getNeTime(song['length'])
            except:
                r_dict['duration'] = None
            r_dict['artist_id'] = song['artist_id']
            r_dict['artist'] = song['artist_name']
            r_dict['artist_pic'] = song['artist_logo']
            r_dict['album_id'] = song['album_id']
            r_dict['album'] = song['album_name']
            r_dict['album_pic'] = song['album_logo']
            try:
                r_dict['lyric'] = song['lyric']
            except BaseException:
                r_dict['lyric'] = None
            r_dict['needPayFlag'] = song['need_pay_flag']
            result_dict['songs'].append(r_dict)

        q.put_nowait(result_dict)

    def search(self, target):
        q = queue.Queue()
        t1 = Thread(target=self.searchQQ,args=(target,q))
        t2 = Thread(target=self.searchNetease,args=(target,q))
        t3 = Thread(target=self.searchKuwo,args=(target,q))
        t4 = Thread(target=self.searchXiami,args=(target,q))
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        first = q.get()
        second = q.get()
        third = q.get()
        fourth = q.get()
        res = {
            'error': 0,
            'msg': 'success',
            'data': {
                'target': target,
                first['source']: first,
                second['source']: second,
                third['source']: third,
                fourth['source']: fourth
            }
        }
        return res
