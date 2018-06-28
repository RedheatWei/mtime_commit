#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@auther = 'Redheat'
@create = '2018/6/28 18:15'
@email = 'qjyyn@qq.com'
'''
import requests
from bs4 import BeautifulSoup
import re
import sqlite3

def get_url_list():
    a_list = []
    for i in range(1,166):
        url = 'http://movie.mtime.com/movie/search/section/?year=2017&pageIndex=%s' % i
        print(url)
        r = requests.get(url)
        soup = BeautifulSoup(r.content,'lxml')
        all_a = soup.find_all(href=re.compile("\d{5,}"))
        for a in all_a:
            a_list.append(a.get('href'))
        return a_list
a_list = get_url_list()

def insertIntoDb():
    conn = sqlite3.connect('test.db')