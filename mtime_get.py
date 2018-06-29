#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@auther = 'Redheat'
@create = '2018/6/28 18:15'
@email = 'qjyyn@qq.com'
'''
from selenium import webdriver
import selenium.webdriver.chrome.service as chrome_service
import sqlite3
import time


class OpenUrl(object):
    def __init__(self):
        service = chrome_service.Service('/Users/Redheat/Library/chromedriver/chromedriver')
        service.start()
        capabilities = {'chrome.binary': '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'}
        self.driver = webdriver.Remote(service.service_url, capabilities)

    def open_url(self, page):
        self.driver.get('http://movie.mtime.com/movie/search/section/?year=2017&pageIndex=%s' % page)
        urls = self.driver.find_elements_by_xpath("//h3[@class='normal mt6']/a")
        return [url.get_attribute("href") for url in urls]
    def __del__(self):
        self.driver.quit()

class ProcessDb(object):
    def __init__(self,dbname):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()
    def insert(self,url_list):
        for url in url_list:
            self.cursor.execute('insert or ignore  into urls (url, time_year) values ("%s","%s")' % (url, 2017))
    def __del__(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()
# def open_url(driver, page):
#     driver.get('http://movie.mtime.com/movie/search/section/?year=2017&pageIndex=%s' % 1)
#     urls = driver.find_elements_by_xpath("//h3[@class='normal mt6']/a")
#     return [url.get_attribute("href") for url in urls]


# def insertIntoDb(url_list):
#     conn = sqlite3.connect('mtime.db')
#     cursor = conn.cursor()
#     for url in url_list:
#         cursor.execute('insert or ignore  into urls (url, time_year) values (%s,%s)' % (url, 2017))
#     cursor.close()
#     conn.commit()
#     conn.close()


# def create_dirver():
#     service = chrome_service.Service('/Users/Redheat/Library/chromedriver/chromedriver')
#     service.start()
#     capabilities = {'chrome.binary': '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'}
#     dirver = webdriver.Remote(service.service_url, capabilities)
#     return dirver

driver = OpenUrl()
db = ProcessDb("mtime.db3")
for page in range(8, 166):
    print(page)
    time.sleep(3)
    url_list = driver.open_url(page)
    db.insert(url_list)
