import asyncio
from aiohttp import ClientSession
import time
import math
import queue,json

def getNeTime(ms):
    s = ms / 1000
    mi = s // 60
    se = s % 60
    return '%02d:%02d' % (mi, se)
# class MusicSearcher():
async def searchKuwo(target):
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

    async with ClientSession() as session:
        async with session.get(url,params=params,headers=headers) as response:
            res = await response.read()
            search_res_dict = json.loads(res)
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
            return result_dict



async def searchXiami(target):
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
    async with ClientSession() as session:
        async with session.get(search_url,params=params,headers=headers) as response:
            res = await response.text()
            print(res)
            search_res_dict = json.loads(res)
            # result_dict = {
            #     "source": 'xiami',
            #     "paginate": {
            #         "page": int(params['page']),
            #         "pagesize": int(params['limit']),
            #         "pages": int(math.ceil(int(search_res_dict['data']['total']) / int(params['limit']))),
            #         "count": int(search_res_dict['data']['total'])
            #     },
            #     "songs": []
            # }
            # for song in search_res_dict["data"]["songs"]:
            #     r_dict = {}
            #     r_dict['source'] = 'xiami'
            #     r_dict['name'] = song['song_name']
            #     r_dict['song_id'] = song['song_id']
            #     try:
            #         r_dict['duration'] = getNeTime(song['length'])
            #     except:
            #         r_dict['duration'] = None
            #     r_dict['artist_id'] = song['artist_id']
            #     r_dict['artist'] = song['artist_name']
            #     r_dict['artist_pic'] = song['artist_logo']
            #     r_dict['album_id'] = song['album_id']
            #     r_dict['album'] = song['album_name']
            #     r_dict['album_pic'] = song['album_logo']
            #     try:
            #         r_dict['lyric'] = song['lyric']
            #     except BaseException:
            #         r_dict['lyric'] = None
            #     r_dict['needPayFlag'] = song['need_pay_flag']
            #     result_dict['songs'].append(r_dict)

            # return result_dict


if __name__ == '__main__':
    # q = queue.Queue()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(searchKuwo('radiohead',q))
    # first = q.get()
    # second = q.get()
    # print(first)
    # print(second)
    tasks = []
    task1 = asyncio.ensure_future(searchKuwo('radiohead'))
    task2 = asyncio.ensure_future(searchXiami('radiohead'))
    tasks.append(task1)
    tasks.append(task2)
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(asyncio.gather(*tasks))
