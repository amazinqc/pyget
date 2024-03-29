#!/usr/bin/evn/python3
# -*- coding: utf-8 -*-
import re, requests, json
from random import random
from coredown import pyget
# from decorat import test

import urllib3
urllib3.disable_warnings()

#    ↓↓ 博客主页：http://blog.sina.com.cn/s/articlelist_6055728941_0_{{page}}.html
#    ↓↓ 音乐子页：http://blog.sina.com.cn/s/blog_{{blogid}}.html
#    ↓↓ 城通网站：https://545c.com/file/{{userid}}-{{fileid}}  <<<==太傻逼了
#    ↓↓ js互动获取downurl：详见blogmusic.info    <<<==已解决

cki = 'PHPSESSID=v455tlbfm23kkk2bbogoes27g3'
api_server = 'https://webapi.400gb.com'
sinablog = 'http://blog.sina.com.cn/s/articlelist_6055728941_0_%d.html'
cookie = None
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
    'Collection': 'Keep-alive'
}

def getHTML(url, i=1, n=0):
    global cookie
    headers['Referer'] = sinablog % i
    try:
        h = requests.get(url, headers=headers, cookies=cookie, verify=False)
        h.encoding = 'utf-8'
        cookie = h.cookies
        return h.text
    except:
        if n<6:
            if n >3:
                cookie = None
            print('Waiting for retrying with %d times...\n\turl:' % (n+1), url)
            return getHTML(url, i, n+1)
        else:
            print('Connection Timeout WTF???')
            return ''
            # raise
  
def getBlog(page=1):    #找到主博客下的资源博客
    blog = sinablog % page
    print('Start searching the page %d...' % page)
    html = getHTML(blog)
    reblog = r'(?is)<span class="atc_title">.*?href="(.*?)">.*?</a></span>'
    return re.finditer(reblog, html)  #返回一个迭代器

def getMusic(mbs, i=1):    #找到资源博客下的城通网盘链接信息,返回迭代信息
    for mb in mbs:
        mblog = mb.group(1)
        mhtml = getHTML(mblog, i)
        recity = r'(?is)<a href="(https?://.*?/(\d+)-(\d+))".*?>\1</a>'
        cityurl = re.search(recity, mhtml)
        if cityurl:
            _, uid, fid = cityurl.groups()
            yield uid, fid
        else:
            with open('file.txt', 'a+') as f:
                f.write(str(i) + ': ' + mblog + '\n')

def getJSON(url, uid, fid, pms=None):
    global cki
    h = dict(headers)
    h["Referer"] = 'https://545c.com/file/%s-%s' % (uid, fid)
    h['Host'] = 'webapi.400gb.com'
    h['Origin'] = 'https://545c.com/file'
    h['Cookie'] = cki
    r = requests.get(url, params=pms, headers=h, verify=False)
    cki = r.headers.get('Set-Cookie', cki)
    try:
        j = r.json()
    except:
        try:
            j = json.loads(r.text)
        except:
            print('Unjson:', r.text)
            j = {}
    return j

def getMSG(uid, fid, ref='', n=0):
    url = api_server + '/getfile.php'
    kvs = {'f': '%s-%s' % (uid, fid), 'ref': ref}
    j = getJSON(url, uid, fid, kvs)
    fn = j.get('file_name')
    #fs = j['file_size']
    fc = j.get('file_chk')
    #uid = j['userid']
    #fid = j['file_id']
    if (fn and fc) is None:
        if j.get('code') == 200 and n < 2:
            return getMSG(uid, fid, n=n+1)
    return fn, fc

def getURL(uid, fid, fchk, n=0):
    url = api_server + '/get_file_url.php'
    kvs = {'uid': uid, 'fid': fid, 'folder_id': 0, 'file_chk': fchk, 'mb': 0, 'app': 0, 'acheck': 1, 'verifycode': '', 'rd': random()}
    j = getJSON(url, uid, fid, kvs)
    durl = j.get('downurl')
    if (durl is None) and n < 3:
        return getURL(uid, fid, fchk, n+1)
    return durl

def spider():
    path = r'G:\blogmusic'
    for i in range(1, 64):
        if i in list(range(2,23)):
            continue
        for u, f in getMusic(getBlog(i), i):
            fn, fc = getMSG(u, f)
            if (fn or fc) is None:      # j['code'] != 200
                print('%s-%s is missing ...' % (u, f))
                with open('file.txt', 'a+') as fl:
                    fl.write(str(u) + '-' + str(f) + '\n')
                continue
            if pyget('', path, fname=fn).doFile():
                print('<%s> is existed' % fn)
                continue
            r = pyget(getURL(u, f, fc), path, fname=fn).download()
            if r is False:
                print('get', str(r), 'to stop the pyget')
                return
if __name__ == "__main__":
    spider()