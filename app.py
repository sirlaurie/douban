#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: loricheung
import requests
import execjs
import re
from urllib import parse
from flask import Flask
from flask import jsonify

app = Flask(__name__)
execjs.runtimes = 'Node'

book_url = 'https://search.douban.com/book/subject_search?search_text={title}&cat=1001'
movie_url = 'https://search.douban.com/movie/subject_search?search_text={title}&cat=1002'
headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    'accept-language': "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
    'cookie': 'll="108296"; bid=ieDyF9S_Pvo; __utma=30149280.1219785301.1576592769.1576592769.1576592769.1; __utmc=30149280; __utmz=30149280.1576592769.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _vwo_uuid_v2=DF618B52A6E9245858190AA370A98D7E4|0b4d39fcf413bf2c3e364ddad81e6a76; ct=y; dbcl2="40219042:K/CjqllYI3Y"; ck=FsDX; push_noty_num=0; push_doumail_num=0; douban-fav-remind=1; ap_v=0,6.0',
    'host': "search.douban.com",
    'referer': "https://movie.douban.com/",
    'sec-fetch-mode': "navigate",
    'sec-fetch-site': "same-site",
    'sec-fetch-user': "?1",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36 Edg/79.0.309.56"
    }

@app.route('/')
def hello():
    return '<h3>hello, douban</h3>'


@app.route('/api/<category>/<title>')
def crawl(category, title):
    title = parse.quote(title)
    if str(category) == 'book':
        url = book_url.format(title=title)
    else:
        url = movie_url.format(title=title)
    data = request_from(url)

    result = []
    for index, item in enumerate(data['payload']['items']):
        item_url = item.get('url', '')
        name = item.get('title', '')
        score = item.get('rating', {}).get('value', '暂无评分')
        author = item.get('abstract', '')
        if name and 'subject' in item_url:
            kwargs = {
                'url': item_url,
                'name': name,
                'score': score,
                'author': author
            }
            result.append(kwargs)
    return jsonify(result)


def request_from(url):
    resp = requests.get(url, headers=headers)
    html = re.search('window.__DATA__ = "([^"]+)"', resp.text).group(1)

    with open('main.js', 'r') as f:
        decrypt_js = f.read()
    ctx = execjs.compile(decrypt_js)
    data = ctx.call('decrypt', html)
    return data
