# ##############################################   SOGOU   ##########################################################  
# import requests, time

# kw = input('搜索:\n')
# s = requests.session()
# search_url = "https://songsearch.kugou.com/song_search_v2"

# headers = {
#     'Referer': 'https://www.kugou.com/yy/html/search.html',
#     'Sec-Fetch-Mode': 'no-cors',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
# }

# params = {
#     # 'callback': 'jQuery1124016934115272303574_1565766215568',
#     'keyword': kw,
#     'page': 1,
#     'pagesize': 60,
#     'userid': -1,
#     'clientver': '',
#     'platform': 'WebFilter',
#     'tag': 'em',
#     'filter': 2,
#     'iscorrection': 1,
#     'privilege_filter': 0,
#     '_': int(time.time() * 1000)
# }

# res = s.get(search_url,headers=headers,params=params)
# res.encoding = 'utf-8'
# with open('C:\\Users\\Sevenforty\\Desktop\\res.js','w') as f:
#     f.write(res.text)


# # #######################################################  XIAMI  ###############################################################################
import requests, time,json

kw = input('搜索:\n')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'referer': 'http://m.xiami.com/',
    'Host':'api.xiami.com'
}
search_url = 'http://api.xiami.com/web'

params = {
    "key": kw,
    "v": "2.0",
    "app_key": "1",
    "r": "search/songs",
    "page": 1,
    "limit": 50,
}

res = requests.get(search_url, params=params,headers=headers)
print(res.text)

# url = 'http://api.xiami.com/web'
# params = {
#     "v": "2.0",
#     "app_key": "1",
#     "r": "song/detail",
#     "id": 1795547984,
# }
# res = requests.get(url, params=params, headers=headers)
# res.encoding = "utf-8"
# res = json.loads(res.text)
# url = res['data']['song'].get('listen_file','')
# print(url)

# ####################################  XIAMI  _s _q ###################################################
# def getNeTime(ms):
#     s = ms / 1000
#     mi = s // 60
#     se = s % 60
#     return '%02d:%02d' % (mi, se)


# import requests,json,hashlib
# s = requests.Session()
# s.headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
#     'referer': 'http://m.xiami.com/'
# }

# def encrypted_params(keyword):
#     _q = dict(key=keyword, pagingVO=dict(page=1, pageSize=60))
#     _q = json.dumps(_q)
#     url = "https://www.xiami.com/search?key={}".format(keyword)
#     res = s.get(url)
#     cookie = res.cookies.get("xm_sg_tk", "").split("_")[0]
#     origin_str = "%s_xmMain_/api/search/searchSongs_%s" % (cookie, _q)
#     _s = hashlib.md5(origin_str.encode()).hexdigest()
#     return dict(_q=_q, _s=_s)


# def xiami_search(keyword):
#     params = encrypted_params(keyword=keyword)
#     res = s.get("https://www.xiami.com/api/search/searchSongs",params=params)
#     res.encoding = "utf-8"
#     res = json.loads(res.text)
#     return res

# kw = input('搜索关键词\n')
# r = xiami_search(kw)
# print(r)


# r_d = {
#     "songs":[]
# }
# for song in r["result"]["data"]["songs"]:
#     r_dict = {}
#     r_dict['source'] = 'xiami'
#     r_dict['name'] = song['songName']
#     r_dict['song_id'] = song['songId']
#     r_dict['duration'] = getNeTime(song['length'])
#     r_dict['artist_id'] = song['artistId']
#     r_dict['artist'] = song['artistName']
#     r_dict['artist_pic'] = song['artistLogo']
#     r_dict['album_id'] = song['albumId']
#     r_dict['album'] = song['albumName']
#     r_dict['album_pic'] = song['albumLogo']
#     try:
#         r_dict['lyric'] = song['lyricInfo']['lyricFile']
#     except BaseException:
#         r_dict['lyric'] = None
#     r_dict['needPayFlag'] = song['needPayFlag']
#     r_d['songs'].append(r_dict)
# print(r_d)
# for song in r_d['songs']:
#     song_id = song['song_id']
#     url = 'http://api.xiami.com/web'
#     params = {
#         "v": "2.0",
#         "app_key": "1",
#         "r": "song/detail",
#         "id": song_id,
#     }
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
#         'referer': 'http://m.xiami.com/'
#     }
#     res = requests.get(url,params=params,headers=headers)
#     res.encoding="utf-8"
#     d = json.loads(res.text)
#     lyric_file = d['data']['song'].get('lyric')
#     lres = requests.get(lyric_file,headers=headers)
#     print(lres.text)
# import re
# with open("C:\\Users\\Sevenforty\\Desktop\\lyric.txt","r") as f:
#     lyric = f.read()

# r = re.sub(r'<\d+?>','',lyric,flags=re.S)
# print(r)


# import requests
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
#     'referer': 'http://m.xiami.com/'
# }
# res = requests.get("http://img.xiami.net/lyric/84/1795547984_1498829184_1119.trc",headers=headers)

# print(res.text)

