#!/usr/bin/evn/python3
# -*- coding: utf-8 -*-
import re, requests, json, time
from random import random
from coredown import pyget



#    ↓↓ 博客主页：http://blog.sina.com.cn/s/articlelist_6055728941_0_{{page}}.html
#    ↓↓ 音乐子页：http://blog.sina.com.cn/s/blog_{{blogid}}.html
#    ↓↓ 城通网站：https://545c.com/file/{{userid}}-{{fileid}}  <<<==太傻逼了
#    ↓↓ js互动获取downurl：详见blogmusic.info    <<<==已解决

api_server = 'https://webapi.400gb.com'
sinablog = 'http://blog.sina.com.cn/s/articlelist_6055728941_0_%d.html'
cookie = None
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
}
def getHTML(url, i=None, n=0):
    global cookie
    headers['Referer'] = None
    print('Waiting for the %d times...' % (n+1))
    try:
        h = requests.get(url, headers=headers, cookies=cookie)
        h.encoding = 'utf-8'
        cookie = h.cookies
        return h.text
    except:
        if n<4:
            print('Retry to url:', url)
            return getHTML(url, i, n+1)
        elif n<6:
            cookie = None
            print('Retry to url:', url)
            return getHTML(url, i, n+1)
        else:
            print('Connection Timeout WTF???')
            # raise
    
    

def getBlog(page=1):    #找到主博客下的资源博客
    blog = sinablog % page
    print('Start searching the page %d...' % page)
    html = getHTML(blog)
    reblog = r'(?is)<span class="atc_title">.*?href="(.*?)">.*?</a></span>'
    return re.finditer(reblog, html)  #返回一个迭代器

def getMusic(mbs):    #找到资源博客下的城通网盘链接信息,返回迭代信息
    i = 1
    for mb in mbs:
        mblog = mb.group(1)
        mhtml = getHTML(mblog, i)
        i += 1
        recity = r'(?is)<a href="(https://.*?/(\d+)-(\d+))".*?>\1</a>'
        cityurl = re.search(recity, mhtml)
        _, uid, fid = cityurl.groups()
        yield uid, fid

def getJSON(url, pms=None):
    r = requests.get(url, params=pms, headers=headers)
    j = r.json()
    return j

def getMSG(uid, fid, ref=''):
    url = api_server + '/getfile.php'
    kvs = {'f': '%s-%s' % (uid, fid), 'ref': ref}
    j = getJSON(url, kvs)
    fn = j['file_name']
    #fs = j['file_size']
    fc = j['file_chk']
    #uid = j['userid']
    #fid = j['file_id']
    return fn, fc

def getURL(uid, fid, fchk):    #待定**kw可使用"kw.get(key) or default"
    url = api_server + '/get_file_url.php'
    kvs = {'uid': uid, 'fid': fid, 'folder_id': 0, 'file_chk': fchk, 'mb': 0, 'app': 0, 'acheck': 1, 'verifycode': '', 'rd': random()}
    j = getJSON(url, kvs)
    durl = j.get('downurl')
    return durl

def spider():
    path = r'C:\Users\15520\Music\blogmusic'
    for i in range(1, 8):
        for u, f in getMusic(getBlog(i)):
            fn, fc = getMSG(u, f)
            pyget(getURL(u, f, fc), path, fname=fn).download()

spider()