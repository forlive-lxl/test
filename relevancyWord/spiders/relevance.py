import scrapy
from scrapy_redis.spiders import RedisSpider
import json
from relevancyWord.items import RelevancywordItem


# class RelevanceSpider(scrapy.Spider):
class RelevanceSpider(RedisSpider):
    name = 'relevance'
    # allowed_domains = ['www.xiapi.com']
    # start_urls = ['http://www.xiapi.com/']
    redis_key = 'search_word:start_urls'

    def parse(self, response):
        task_url = response.url
        relevancykords = [i['keyword'] for i in json.loads(response.text)['keywords']]
        res = json.dumps(relevancykords)
        item = RelevancywordItem(task_url=task_url, res=res)
        yield item