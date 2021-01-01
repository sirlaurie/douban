#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: loricheung
import sys
import requests
import execjs
import re
from urllib import parse
from flask import Flask
from flask import jsonify

app = Flask(__name__)
execjs.runtimes = "Node"

book_url = "https://search.douban.com/book/subject_search?search_text={title}&cat=1001"
movie_url = (
    "https://search.douban.com/movie/subject_search?search_text={title}&cat=1002"
)
default_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'bid=g45DUsaXGO4; ll="108296"; push_doumail_num=0; push_noty_num=0; douban-fav-remind=1; _vwo_uuid_v2=DD838DB5809029D29EA2682C7BD69CDA3|c0bdf5263233b42569c736b90c28f8c7; viewed="2308234_27615777"; dbcl2="40219042:PKtobXAqaRs"; ck=T7Vf; douban-profile-remind=1; ap_v=0,6.0',
    'Host': 'search.douban.com',
    'Referer': 'https://movie.douban.com/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    }


@app.route("/")
def hello():
    return "<h3>hello, douban</h3>"


@app.route("/api/<category>/<title>")
def crawl(category, title):
    title = parse.quote(title)
    if str(category) == "book":
        url = book_url.format(title=title)
    else:
        url = movie_url.format(title=title)
    data = request_from(url)

    result = []
    for index, item in enumerate(data["payload"]["items"]):
        item_url = item.get("url", "")
        name = item.get("title", "")
        score = item.get("rating", {}).get("value", "暂无评分")
        author = item.get("abstract", "")
        if name and "subject" in item_url:
            kwargs = {
                "id": item_url.split("/")[-2],
                "url": item_url,
                "name": name,
                "score": score,
                "author": author,
            }
            result.append(kwargs)
    return jsonify(result)


def request_from(url):
    headers = default_headers
    headers.update({"Referer": url})
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        html = re.search('window.__DATA__ = "(.+)"', resp.text).group(1)
    else:
        sys.exit("response status code: ", resp.status_code)

    with open("main.js", "r") as f:
        decrypt_js = f.read()
    ctx = execjs.compile(decrypt_js)
    data = ctx.call("decrypt", html)
    return data


if __name__ == '__main__':
    with app.app_context():
        print(crawl('movie', 'togo'))
