#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: loricheung
import os
import math
import json
import argparse
import urllib
import urllib2
from alfred.feedback import Feedback


headers = {
    'Host': 'frodo.douban.com',
    'Content-Type': 'application/json',
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'User-Agent':' Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
    'Referer': 'https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html',
    'Accept-Language':' en-us',
    'Cookie': 'll="108296"; bid=iytqR0heGuI'
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
        if "?" in url:
            url = url.split('?')[0]
        os.system('curl --parallel --no-progress-meter --output-dir cache -O ' + url)
        # os.system('curl -O ' + CACHE_FOLDER + cover + ' ' + url)

    def search(self, keyword):
        request = urllib2.Request("https://frodo.douban.com//api/v2/search/weixin?start=0&count=20&apiKey=0ac44ae016490db2204ce0a042db2916&q=" + urllib.quote(keyword), None, headers)
        response = urllib2.urlopen(request)
        result = response.read().decode("utf-8")

        data = json.loads(result)
        # print data
        feedback = Feedback()
        for item in data['items']:
            target_type = item["target_type"]
            if target_type not in target_url.keys():
                continue
            url = target_url[target_type] + item["target"]["id"]
            cover_url = item['target']['cover_url']
            if '?' in cover_url:
                cover_url = cover_url.split('?')[0]
            cover = cover_url.split('/')[-1].encode('utf-8')
            self._download_thumb(cover_url)
            title = item["target"]["title"]
            # value = item["target"]["rating"]["value"]
            star = item["target"]["rating"]["star_count"]
            info = item["target"]["card_subtitle"]
            decimal, integer = math.modf(float(star))
            if decimal != 0.0:
                star_info = (int(integer) * '★').decode('utf-8') + '☆'.decode('utf-8')
            else:
                star_info = (int(integer) * '★').decode('utf-8')
            icon = os.path.join(cache_folder, cover)
            feedback.addItem(title=title + u' ' + star_info, subtitle=info, arg=url, type=target_type, icon=icon)

        feedback.output()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('search', type=str)
    args = parser.parse_args()
    if args.search == 'c':
        clear()
    else:
        douban = Douban()
        douban.search(args.search)
