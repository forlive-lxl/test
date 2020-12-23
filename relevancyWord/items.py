# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RelevancywordItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    task_url = scrapy.Field()
    res = scrapy.Field()
