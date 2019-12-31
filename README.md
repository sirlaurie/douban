# douban
爬虫实现的豆瓣电影检索API

### requirements
    flask
    execjs
    requests

`pip3 install flask requests PyExecJS -i https://pypi.douban.com/simple`

### 使用方法

1.   克隆项目到本地

2.   安装Nginx

    brew install nginx

3.   安装uwsgi

    pip3 install uwsgi -i https://pypi.douban.com/simple

3.   找到下面配置并修改 `/etc/local/etc/nginx/nginx.conf` (路径替换为实际的路径):

         location / {
             include uwsgi_params;
             uwsgi_pass unix:/path/to/doubanapi/douban.sock;
         }

4.  启动服务

    `uwsgi --ini wsgi.ini`

    `brew services restart nginx`

5.  打开浏览器, 输入 http://127.0.0.1/api/movie/togo (可替换togo为任意电影名, 中英文都可)测试
