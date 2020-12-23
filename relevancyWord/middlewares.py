# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from fake_useragent import UserAgent
from twisted.internet.defer import DeferredLock
from twisted.internet.error import TimeoutError,TCPTimedOutError
import requests
import json
import time
from collections import defaultdict


class RelevancywordSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RelevancywordDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class UserAgentDownloadMiddleware(object):
    ua = UserAgent()
    user_agent = ua.chrome
    headers = None

    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.user_agent
        return None

# 下载中间件
class IPProxyDownloadMiddleware(object):
    def __init__(self):
        super(IPProxyDownloadMiddleware,self).__init__()
        self.current_proxy = None
        self.lock = DeferredLock()
        self.accessed_proxies = []
        self.succeed_crawl_count = 0
        self.http_https = 0
        self.blacked = 1
        self.url_count = 0

    def process_request(self, request, spider):
        try:
            p = request.meta['proxy'] 
        except:
            self.url_count += 1
            print('Total need to be crawled url numbers：', self.url_count)
        if self.current_proxy == None or self.blacked == 1:
            self.update_proxy()
        request.meta['proxy'] = self.current_proxy
        request.dont_filter = True
        return None

    def process_response(self, request, response, spider):
        if response.status != 200:
            print('-' * 50)
            print("%s这个代理被加入黑名单" % request.meta['proxy'])
            print('-' * 50)
            if request.meta['proxy'] == self.current_proxy:
                self.blacked = 1
            return request

        elif 'https://shopee.com.my/api/v2/search_items/?by=relevancy&limit=50&match_id=' in request.url:
            data = json.loads(response.text)
            for i in data.get("items"):
                if len(i.get("image")) != 32:
                    print('-.-' * 50)
                    print("返回数据错误！重新爬取...")
                    print('-.-' * 50)
                    if request.meta['proxy'] == self.current_proxy:
                        self.blacked = 1
                    return request

        self.blacked = 0
        self.current_proxy = request.meta['proxy']
        self.succeed_crawl_count += 1
        print('-*-' * 50)
        print("当前请求URL:", request)
        print("当前请求使用代理IP:", self.current_proxy)
        print('=====成功爬取了{}个URL====='.format(self.succeed_crawl_count))
        print('-*-' * 50)
        return response

    def process_exception(self, request, exception, spider):
        print('-' * 50)
        print("{}！重新获取代理ip...".format(exception))
        print('-' * 50)
        if request.meta['proxy'] == self.current_proxy:
            self.blacked = 1
        return request

    def update_proxy(self):
        self.lock.acquire()
        if self.http_https == 0:
            proxy_str = requests.get('http://127.0.0.1:5555/random').text
            proxy = 'https://' + proxy_str
            self.current_proxy = proxy
            self.http_https = 1
        else:
            proxy = 'http://' + self.current_proxy[8:]
            self.current_proxy = proxy
            self.http_https = 0
        self.lock.release()
