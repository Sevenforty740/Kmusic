import requests
from concurrent.futures import ThreadPoolExecutor
from .netEaseEncode import *
import urllib.parse
import time
import queue

def getQQTime(s):
    s = s
    mi = s // 60
    se = s % 60
    return '%02d:%02d' % (mi, se)


def getNeTime(ms):
    s = ms/1000
    mi = s//60
    se = s % 60
    return '%02d:%02d'% (mi, se)


class MusicSearcher():
    def searchQQ(self,target,q):
        url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'

        headers = {
            'Accept': '*/*',
            'Connection': 'Keep-Alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'User-Agent': 'Mozilla/5.0(compatible;MSIE 9.0;Windows NT 6.1;WOW64;Trident/5.0)',
            'Host' : 'c.y.qq.com',
            'Referer' : 'c.y.qq.com'
        }

        params = {
            'format' : 'json',
            't' : 0,
            'loginUin' : 0,
            'inCharset' : 'GB2312',
            'outCharset' : 'utf-8',
            'qqmusic_ver' : 1653,
            'catZhida' : 1,
            'p' : 1,
            'n' : 60,
            'w' : urllib.parse.quote(target),
            'flag_qc' : 0,
            'remoteplace' : 'txt.newclient.top',
            'new_json' : 1,
            'auto' : 1,
            'lossless' : 0,
            'aggr' : 1,
            'cr' : 1,
            'sem' : 0,
            'force_zonghe' : 0,
            'pcachetime':int(time.time()),
        }

        res = requests.get(url,params=params,headers=headers)
        r_d = json.loads(res.text)
        r_l = r_d['data']['song']['list']
        resultList = ['qq']
        for song in r_l:
            songDic = {}
            songDic['source'] = 'qq'
            songDic['name'] = song['name']
            songDic['song_id'] = song['mid']
            songDic['duration'] = getQQTime(song['interval'])
            songDic['artist_id'] = song['singer'][0]['id']
            songDic['artist'] = song['singer'][0]['name']
            songDic['album_id'] = song['album']['id']
            songDic['album_mid'] = song['album']['mid']
            songDic['album'] = song['album']['name']
            resultList.append(songDic)

        q.put(resultList)

    def searchNetease(self,target,q):
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

        data = {
            's': target,
            'offset': '0',
            'limit': '60',
            'type': '1'
        }
        data = encrypted_request(data)
        res = requests.post(url,headers=headers,data=data)
        r_d = json.loads(res.text)
        r_l = r_d['result']['songs']
        resultList = ['netease']
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
            resultList.append(songDic)

        q.put_nowait(resultList)


    def searchKuwo(self,target,q):
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
            'reqId': 'b6168da1-a385-11e9-b78e-a5d90de9d862'
        }

        res = requests.get(url,headers=headers,params=params)
        search_res_dict = json.loads(res.text)
        resultList = ['kuwo']
        for song in search_res_dict['data']['list']:
            d = {}
            d['source'] = 'kuwo'
            d['name'] = song['name']
            d['song_id'] = song['rid']
            d['artist'] = song['artist']
            d['artist_id'] = song['artistid']
            d['album'] = song['album']
            d['album_id'] = song['albumid']
            try:
                d['album_pic'] = song['albumpic']
            except:
                pass
            d['duration'] = song['songTimeMinutes']
            resultList.append(d)
        q.put_nowait(resultList)


    def search(self,target):
        q = queue.Queue()
        pool = ThreadPoolExecutor()
        pool.submit(self.searchQQ,target,q)
        pool.submit(self.searchNetease,target,q)
        pool.submit(self.searchKuwo,target,q)
        pool.shutdown(wait=True)
        first = q.get()
        second = q.get()
        third = q.get()
        res = {
            'error': 0,
            'msg': None,
            'data': {
                'target': target,
                first[0]: first[1:],
                second[0]: second[1:],
                third[0]: third[1:]
            }
        }

        return res

