from .netEaseEncode import *
import requests
import urllib.parse

class MusicSearcher():
    def __init__(self,target,q):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
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
        self.headers['Host'] = 'c.y.qq.com'
        self.headers['Referer'] = 'https://y.qq.com/portal/playlist.html'

        url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&' + \
              'new_json=1&remoteplace=txt.yqq.center&searchid=43541888870417375&t=0&aggr=1' + \
              '&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=100&' + \
              'w={0}'.format(urllib.parse.quote(self.target)) + \
              '&g_tk=5381&jsonpCallback=searchCallbacksong6064&loginUin=0&hostUin=0&' + \
              'format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'

        response = self.s.get(url,headers=self.headers)
        response = response.text[23:-1]
        r_d = json.loads(response)
        resultList = ['qq']
        for song in r_d['data']['song']['list']:
            songDic = {}
            songDic['songname'] = song['name']
            songDic['songid'] = song['id']
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