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
    def get_details(self, url):
        self.driver.get(url)
        movie_name_div = self.driver.find_element_by_class_name('clearfix')
        # 中文名称
        movie_name_zh = movie_name_div.find_element_by_tag_name("h1").text
        # 英文名称
        try:
            movie_name_en = movie_name_div.find_element_by_class_name("db_enname").text
        except Exception as e:
            movie_name_en = None
            print(e)

        movie_type_div = self.driver.find_element_by_class_name('otherbox')
        # 电影时长
        movie_time = movie_type_div.find_element_by_tag_name('span').text
        # 电影类型
        movie_type_list = [a.text for a in movie_type_div.find_elements_by_tag_name('a')]
        movie_type = '/'.join(movie_type_list[0:-1])
        # 电影上线时间
        movie_online_time = movie_type_list[-1]

        # 电影评分
        movie_score_div = self.driver.find_element_by_id('ratingRegion')
        movie_score_all = movie_score_div.find_element_by_tag_name('b').text.replace("\n", '')

        movie_score_yy = movie_score_div.find_element_by_class_name('yy').find_element_by_tag_name('i').get_attribute(
            'style').replace("width:", "").replace("%;", "")
        movie_score_hm = movie_score_div.find_element_by_class_name('hm').find_element_by_tag_name('i').get_attribute(
            'style').replace("width:", "").replace("%;", "")
        movie_score_dy = movie_score_div.find_element_by_class_name('dy').find_element_by_tag_name('i').get_attribute(
            'style').replace("width:", "").replace("%;", "")
        movie_score_gs = movie_score_div.find_element_by_class_name('gs').find_element_by_tag_name('i').get_attribute(
            'style').replace("width:", "").replace("%;", "")
        details = {
            "movie_name_zh": movie_name_zh,
            "movie_name_en": movie_name_en,
            "movie_time": movie_time,
            "movie_type": movie_type,
            "movie_online_time": movie_online_time,
            "movie_score_all": movie_score_all,
            "movie_score_yy": movie_score_yy,
            "movie_score_hm": movie_score_hm,
            "movie_score_dy": movie_score_dy,
            "movie_score_gs": movie_score_gs,
            "url": url
        }
        return details

    # 获取评论数据
    def get_commit(self, url, page):
        if page == 1:
            url += 'reviews/short/new.html'
        else:
            url += 'reviews/short/new-%s.html' % page
        self.driver.get(url)
        print(url)
        commit_div = self.driver.find_element_by_id('tweetRegion')
        dd_list = commit_div.find_elements_by_tag_name('dd')
        commit_list = []
        for dd in dd_list:
            commit_details = {}
            commit_details['url'] = url
            commit_details['commit'] = dd.find_element_by_tag_name('h3').text
            commit_details['userneck'] = dd.find_element_by_class_name('px14').find_element_by_tag_name('a').text
            commit_details['score'] = dd.find_element_by_tag_name('span').text
            commit_details['commit_time'] = dd.find_element_by_class_name('mt10').find_element_by_tag_name(
                'a').get_attribute('entertime')
            commit_list.append(commit_details)
        return commit_list
        # def __del__(self):
        #     self.driver.quit()


class ProcessDb(object):
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()

    # 查询是否在数据库中
    def isIn(self, url):
        self.cursor.execute('SELECT * FROM details WHERE url="%s"' % url)
        return self.cursor.fetchall()

    # 查询url
    def select_urls(self):
        self.cursor.execute('SELECT * FROM urls')
        return self.cursor.fetchall()

    # 把url插入到数据库
    def insertUrls(self, url_list, year):
        for url in url_list:
            self.cursor.execute('insert or ignore  into urls (url, time_year) values ("%s","%s")' % (url, year))

    # 插入详细信息
    def insertDetails(self, details):
        try:
            self.cursor.execute(
                '''insert or ignore  into details(
                url, movie_name_zh,movie_name_en,movie_time,movie_type,movie_online_time,
                movie_score_all,movie_score_yy,movie_score_hm,movie_score_dy,movie_score_gs
                ) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' % (
                    details['url'], details['movie_name_zh'], details['movie_name_en'], details['movie_time'],
                    details['movie_type'],
                    details['movie_online_time'], details['movie_score_all'], details['movie_score_yy'],
                    details['movie_score_hm'], details['movie_score_dy'],
                    details['movie_score_gs']
                )
            )
        except Exception as e:
            print(e)

    # 插入评论信息
    def insertCommit(self, commit_list):
        for commit in commit_list:
            self.cursor.execute('insert or ignore  into commit('
                                'url, commit,userneck,score,commit_time'
                                ') values ("%s","%s","%s","%s","%s")' % (
                                    commit['url'], commit['commit'], commit['userneck'], commit['score'],
                                    commit['commit_time'],))

    def __del__(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()


# 逻辑函数
class Collect():
    def __init__(self):
        self.driver = OpenUrl()
        self.db = ProcessDb("mtime.db3")

    # 收集url
    def urls(self):
        year = 2012
        max_page = self.driver.page_range(year)
        for page in range(81, max_page + 1):
            print(page)
            url_list = self.driver.get_urls(year, page)
            self.db.insertUrls(url_list, year)

    # 收集详细信息
    def details(self):
        urls = self.db.select_urls()
        for url_list in urls:
            url = url_list[1]
            print(url)
            if not self.db.isIn(url):
                details = self.driver.get_details(url)
                self.db.insertDetails(details)

    # 评论内容
    def commit(self):
        urls = self.db.select_urls()
        for url_list in urls:
            url = url_list[1]
            for page in range(1, 11):
                commit_list = self.driver.get_commit(url, page)
                self.db.insertCommit(commit_list)


collect = Collect()
collect.commit()
