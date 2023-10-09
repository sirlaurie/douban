#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: loricheung
import os
import re
import math
import json
import urllib
import argparse
from alfred.feedback import Feedback


headers = {
    'Host': 'frodo.douban.com',
    'Content-Type': 'application/json',
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'User-Agent':' Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
    'Referer': 'https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html',
    'Accept-Language':' en-us',
}

search_mode = {
    "v": ['movie', 'tv'],
    "s": ['music'],
    "b": ['book'],
    "o": ['app', 'game', 'event', 'drama'],
    "p": ['person'],
    "all": ['movie', 'tv', 'music', 'book', 'app', 'game', 'event', 'drama', 'person']
}

target_url = {
    "movie": "https://movie.douban.com/subject/",
    "book": "https://book.douban.com/subject/",
    "tv": "https://movie.douban.com/subject/",
    "music": "https://music.douban.com/subject/",
    "app": "https://www.douban.com/app/",
    "game": "https://www.douban.com/game/",
    "event": "https://www.douban.com/event/",
    "drama": "https://www.douban.com/drama/",
}

participant = {
    'movie': 1,
    'book': 2,
    'tv': 3,
    'music': 4,
    'app': 5,
    'game': 6,
    'event': 7,
    'drama': 8,
    'person': 9,
    'doulist_cards': 10
}

def sorter(item):
    try:
        value = item['target']['rating']['value']
    except:
        value = -1
    try:
        year = item['target']['year']
    except:
        year = -1
    return (participant[item['target_type']], -int(year), -float(value))


cache_folder = 'cache'
if not os.path.exists(cache_folder):
    os.mkdir(cache_folder)


def clear():
    for root, _, files in os.walk(cache_folder):
        for name in files:
            os.remove(os.path.join(cache_folder, name))
        os.removedirs(root)


class Douban(object):
    def __init__(self):
        for _, _, files in os.walk(cache_folder):
            for name in files:
                os.remove(os.path.join(cache_folder, name))

    def __del__(self):
        pass

    def _download_thumb(self, url):
        url = re.sub(r"(?<=https://).*?/view", "img2.doubanio.com/view", url)
        return os.system('nohup curl --parallel --no-progress-meter --output-dir cache -O %s &' % url)

    def search(self, keyword, mode=None):
        request = urllib.request.Request(f"https://frodo.douban.com/api/v2/search/weixin?q={urllib.parse.quote(keyword)}&start=0&count=20&apiKey=0ac44ae016490db2204ce0a042db2916", data=None, headers=headers)
        response = urllib.request.urlopen(request)
        result = response.read().decode("utf-8")
        data = json.loads(result)
        feedback = Feedback()
        if data['count'] > 0:
            for item in data['items']:
                target_type = item["target_type"]
                if mode:
                    query_mode = search_mode[mode]
                else:
                    query_mode = search_mode['all']

                if (target_type in target_url.keys() and target_type in query_mode):
                    url = target_url[target_type] + item["target"]["id"]
                    cover_url = item['target']['cover_url']
                    if '?' in cover_url:
                        cover_url = cover_url.split('?')[0]
                    cover = cover_url.split('/')[-1]
                    _ = self._download_thumb(cover_url)
                    title = item["target"]["title"]
                    info = item["target"]["card_subtitle"]
                    try:
                        star = item["target"]["rating"]["star_count"]
                    except TypeError:
                        star = 0.0
                    decimal, integer = math.modf(float(star))
                    if decimal != 0.0:
                        star_info = (int(integer) * '★') + '☆'
                    else:
                        star_info = (int(integer) * '★')
                    icon = os.path.join(cache_folder, cover)
                    feedback.addItem(title=title + u' ' + star_info, subtitle=info, arg=url, icon=icon)
        if len(feedback) == 0:
            feedback.addItem(uid='0', title=u'未能搜索到结果, 请通过豆瓣搜索页面进行搜索', subtitle=u'按下回车键, 跳转到豆瓣', arg=u'https://search.douban.com/movie/subject_search?search_text=%s&cat=1002' % urllib.quote(keyword), icon='icon.png')
        feedback.output()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('search', type=str)
    args = parser.parse_args()

    if args.search == 'c':
        clear()

    douban = Douban()
    all_args = args.search.split()
    if len(all_args) > 1:
        mode, kw = all_args[0], all_args[1:]
        if mode in search_mode.keys():
            douban.search(keyword=' '.join(kw), mode=mode)
        else:
            douban.search(keyword=args.search)
    else:
        douban.search(keyword=args.search)
