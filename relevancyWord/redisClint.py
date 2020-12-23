MAX_SCORE = 100
MIN_SCORE = 0
INITIAL_SCORE = 10
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = None
REDIS_KEY = 'search_word:start_urls'

import redis
REDIS_CLIENT_VERSION = redis.__version__
IS_REDIS_VERSION_2 = REDIS_CLIENT_VERSION.startswith('2.')


#任务池
class RedisTask(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    def add_zset(self, task, score=INITIAL_SCORE):
        """
        添加任务，设置分数为初始分数
        :param task: 任务
        :param score: 分数
        :return: 添加结果，1表示添加任务成功
        """
        if not self.db.zscore(REDIS_KEY, task):
            if IS_REDIS_VERSION_2:
                return self.db.zadd(REDIS_KEY, score, task)
            return self.db.zadd(REDIS_KEY, {task: score})
        
    def add_list(self, task):
        """
        添加任务，设置分数为初始分数
        :param task: 任务
        :param score: 分数
        :return: 添加结果，1表示添加任务成功
        """
        return self.db.lpush(REDIS_KEY, task)
        
    def update(self, task, score):
        """
        更新任务分数，不存在则创建，存在即更新分数
        :param task: 任务
        :param score: 分数
        :return: 添加结果，0表示更新分数成功，1表示添加任务成功
        """
        if IS_REDIS_VERSION_2:
            return self.db.zadd(REDIS_KEY, score, task)
        return self.db.zadd(REDIS_KEY, {task: score})

    def get_task(self):
        """
        按照任务排名最高获取1个任务
        :return: 任务
        """
        result = self.db.zrevrange(REDIS_KEY, MIN_SCORE, MAX_SCORE)
        if len(result):
            return result[0]
        else:
            return('no task.')

    def exists(self, task):
        """
        判断任务是否存在
        :param task: 任务
        :return: 是否存在
        """
#         print(self.db.zscore(REDIS_KEY, task))
        return not self.db.zscore(REDIS_KEY, task) == None

    def count(self):
        """
        获取任务数量
        :return: 数量
        """
        return self.db.zcard(REDIS_KEY)

    def all_task(self):
        """
        获取全部任务
        :return: 全部任务列表
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
    
    def del_task(self, task):
        """
        根据task名字删除任务
        Parma name: 任务
        :return: 删除结果
        """
        return self.db.zrem(REDIS_KEY, task) == 1
    
    def del_all_task(self):
        """
        删除整个任务池
        :return: 删除结果
        """
        return self.db.delete(REDIS_KEY) == 1




#结果池
class RedisResult(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    def add_hash(self, name, res):
        """
        添加哈希结果
        :param name: 请求url
        :param res: 请求处理结果
        :return: 添加结果，0表示添加任务成功，1表示添加任务成功
        """
        return self.db.hmset(name, res)
    
    def add_string(self, name, res):
        """
        添加字符串结果
        :param name: 请求url
        :param res: 请求处理结果
        :return: 添加结果为True即成功，存在即更新
        """
        return self.db.set(name, res)

    def get_hash_res(self, name):
        """
        根据url名字获取结果
        Parma name: 请求url
        :return: 结果字典
        """
        return self.db.hgetall(name)
    
    def get_string_res(self, name):
        """
        根据url名字获取结果
        Parma name: 请求url
        :return: 结果字符
        """
        return self.db.get(name)
    
    def del_res(self, name):
        """
        根据url名字删除结果
        Parma name: 请求url
        :return: 删除结果
        """
        return self.db.delete(name) == 1
        
    def exists(self, name):
        """
        判断结果是否存在
        :param name: 请求url
        :return: 是否存在
        """
        try:
            return self.get_hash_res(name) != {}
        except:
            return self.get_string_res(name) != None