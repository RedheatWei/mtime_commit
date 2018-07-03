#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@auther = 'Redheat'
@create = '2018/6/28 18:15'
@email = 'qjyyn@qq.com'
'''
from __future__ import absolute_import, unicode_literals
from selenium import webdriver
import selenium.webdriver.chrome.service as chrome_service
import sqlite3
import time


class OpenUrl(object):
    # 创建浏览器
    def __init__(self, proxy=None):
        desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
        if proxy:
            desired_capabilities['proxy'] = {
                "httpProxy": proxy,
                "ftpProxy": proxy,
                "sslProxy": proxy,
                "noProxy": None,
                "proxyType": "MANUAL",
                "class": "org.openqa.selenium.Proxy",
                "autodetect": False
            }
        service = chrome_service.Service('/Users/Redheat/Library/chromedriver/chromedriver')
        service.start()
        desired_capabilities['chrome.binary'] = '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'
        self.driver = webdriver.Remote(service.service_url, desired_capabilities)

    # 获取本年份的页码数
    def page_range(self, year):
        self.driver.get('http://movie.mtime.com/movie/search/section/?year=%s' % year)
        pages = self.driver.find_elements_by_class_name('num')
        page_list = []
        for page in pages:
            page_list.append(int(page.get_attribute('pageindex')))
        return max(page_list)
        # return max([int(page.get_attribute('pageindex')) for page in pages]) #报错,why???

    # 获取本页面电影url
    def get_urls(self, year, page):
        self.driver.get('http://movie.mtime.com/movie/search/section/?year=%s&pageIndex=%s' % (year, page))
        urls = self.driver.find_elements_by_xpath("//h3[@class='normal mt6']/a")
        return [url.get_attribute("href") for url in urls]
    # 获取电影评分等
    def get_details(self,url):
        self.driver.get(url)
        movie_name_div = self.driver.find_element_by_class_name('clearfix')
        #中文名称
        movie_name_zh = movie_name_div.find_element_by_tag_name("h1").text
        #英文名称
        movie_name_en = movie_name_div.find_element_by_class_name("db_enname").text

        movie_type_div = self.driver.find_element_by_class_name('otherbox __r_c_')
        # 电影时长
        movie_time = movie_type_div.find_element_by_tag_name('span').text
        #电影类型
        movie_type = '/'.join(movie_type_div.find_elements_by_tag_name('a')[0:-1].text)
        # 电影上线时间
        movie_online_time = movie_type_div.find_elements_by_tag_name('a')[-1].text

        movie_score_div = self.driver.find_element_by_id('ratingRegion')




    # def __del__(self):
    #     self.driver.quit()


class ProcessDb(object):
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()

    # 把url插入到数据库
    def insertUrls(self, url_list, year):
        for url in url_list:
            self.cursor.execute('insert or ignore  into urls (url, time_year) values ("%s","%s")' % (url, year))

    def __del__(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

class Collect():
    def __init__(self):
        self.driver = OpenUrl("61.152.230.26:8080")
    def urls(self):
        year = 2012
        max_page = self.driver.page_range(year)
        db = ProcessDb("mtime.db3")
        for page in range(81, max_page + 1):
            print(page)
            url_list = self.driver.get_urls(year, page)
            db.insertUrls(url_list, year)

    def details(self):
        url = "http://movie.mtime.com/125424/"
        self.driver.get_details(url)

Collect().details()