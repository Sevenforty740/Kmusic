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
		
        cookie = {
			'qqmusic_gkey' : '92B45FD2E353E84FF288DF16ACE5D5B198CBD33DE8DF7BDF',
			'qqmusic_gtime' : '0',
			'qqmusic_guid' : 'B1E901DA7379A44022C5AF79FDD9CD96',
			'qqmusic_miniversion' : '53',
			'qqmusic_version' : '16',
			'qm_hideuin' : '0',
			'qm_method' : '1'
		}
		
        nowtime = int(time.time())

        url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?format=json&t=0&loginUin=0&inCharset=GB2312&'+\
			  'outCharset=utf-8&qqmusic_ver=1653&catZhida=1&p=1&n=100&'+\
			  'w={}&flag_qc=0&remoteplace=txt.newclient.top&'.format(urllib.parse.quote(self.target)) +\
			  'new_json=1&auto=1&lossless=0&aggr=1&cr=1&sem=0&force_zonghe=0&pcachetime={}'.format(nowtime)

        response = self.s.get(url,headers=self.headers)
        r_d = json.loads(response.text)
        r_l = r_d['data']['song']['list']
        resultList = ['qq']
        for song in r_l:
            songDic = {}
            songDic['songname'] = song['name']
            songDic['songid'] = song['mid']
            songDic['tottime'] = getQQTime(song['interval'])
            songDic['singerid'] = song['singer'][0]['id']
            songDic['singername'] = song['singer'][0]['name']
            songDic['albumid'] = song['album']['id']
            songDic['albumname'] = song['album']['name']
            resultList.append(songDic)

        self.q.put(resultList)


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
        response = self.s.post(url,data=data,headers=self.headers)
        r_d = json.loads(response.text)
        r_l = r_d['result']['songs']

        resultList = ['netease']
        for song in r_l:
            songDic = {}
            songDic['songname'] = song['name']
            songDic['songid'] = song['id']
            songDic['tottime'] = getNeTime(song['dt'])
            songDic['singerid'] = song['ar'][0]['id']
            songDic['singername'] = song['ar'][0]['name']
            songDic['albumid'] = song['al']['id']
            songDic['albumname'] = song['al']['name']
            songDic['albumpic'] = song['al']['picUrl']
            resultList.append(songDic)

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