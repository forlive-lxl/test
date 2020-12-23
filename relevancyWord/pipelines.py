# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from relevancyWord.redisClint import RedisResult


class RelevancywordPipeline:
    def __init__(self):
        self.conn = RedisResult()

    def process_item(self, item, spider):
        self.conn.add_string(item.get('task_url'), item.get('res'))
        return item
