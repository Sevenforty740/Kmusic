from threading import Thread
from .netEaseEncode import *
import requests
import urllib.parse
import time

class MusicSearcher():
    def __init__(self,target,q):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'Keep-Alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        }
        self.target = target
        self.q = q
        self.s = requests.session()
		

    def qqSearch(self):
        self.headers['Accept-Encoding'] = 'gzip, deflate'
        self.headers['Accept-Language'] = 'zh-CN'
        self.headers['Accept'] = '*/*'
        self.headers['User-Agent'] = 'Mozilla/5.0(compatible;MSIE 9.0;Windows NT 6.1;WOW64;Trident/5.0)'
        self.headers['Host'] = 'c.y.qq.com'
        self.headers['Referer'] = 'c.y.qq.com'
		
        # cookie = {
		# 	'qqmusic_gkey' : '92B45FD2E353E84FF288DF16ACE5D5B198CBD33DE8DF7BDF',
		# 	'qqmusic_gtime' : '0',
		# 	'qqmusic_guid' : 'B1E901DA7379A44022C5AF79FDD9CD96',
		# 	'qqmusic_miniversion' : '53',
		# 	'qqmusic_version' : '16',
		# 	'qm_hideuin' : '0',
		# 	'qm_method' : '1'
		# }
		
        nowtime = int(time.time())

        url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?format=json&t=0&loginUin=0&inCharset=GB2312&'+\
			  'outCharset=utf-8&qqmusic_ver=1653&catZhida=1&p=1&n=60&'+\
			  'w={}&flag_qc=0&remoteplace=txt.newclient.top&'.format(urllib.parse.quote(self.target)) +\
			  'new_json=1&auto=1&lossless=0&aggr=1&cr=1&sem=0&force_zonghe=0&pcachetime={}'.format(nowtime)

        response = self.s.get(url,headers=self.headers)
        r_d = json.loads(response.text)
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

        self.q.put(resultList)


    def netEaseSearch(self):
        self.headers['Host'] = 'music.163.com'
        self.headers['Referer'] = 'http://music.163.com/'

        data = {
            's': self.target,
            'offset': '0',
            'limit': '60',
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

        self.q.put(resultList)

    def kuWoSearch(self):
        index_url = 'http://www.kuwo.cn/'
        while True:
            self.s.get(index_url)
            token = dict(self.s.cookies).get('kw_token')
            if token:
                # self.s.headers.update(self.headers)
                self.s.headers.update({'Cookie' : 'kw_token={}'.format(token)})
                self.s.headers.update({'csrf' : token})
                self.s.headers.update({'Referer' : 'http://www.kuwo.cn'})
                break
        search_params = {
            'key': self.target,
            'pn': '1',
            'rn': '60',
            'reqId': 'b6168da1-a385-11e9-b78e-a5d90de9d862'
        }
        search_url = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord'

        res = self.s.get(search_url, params=search_params)
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
        del self.s.headers['Referer']
        del self.s.headers['Cookie']
        del self.s.headers['csrf']
        self.q.put(resultList)


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

