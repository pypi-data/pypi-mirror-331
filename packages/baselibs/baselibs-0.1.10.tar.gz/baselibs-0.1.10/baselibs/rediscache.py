#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

'''
Redis缓存类 v0.2.0
'''

import redis
import json
import logging

class RedisCache():
    def __init__(self, host='127.0.0.1', port=6379, ttl=3600, dat_table="CACHE_TABLE"):
        self.host = host
        self.port = port
        self.pool = None
        self.cline = None
        self.ttl = ttl   # 默认过期时间（秒）, 0=永不过期，默认=3600s=1小时

        # 表名称
        self.dat_table = dat_table
        self.connect_redis()

    def connect_redis(self):
        ''' 连接Redis
        '''

        try:
            pool = redis.ConnectionPool(host=self.host,
                    port=self.port, max_connections=50,
                    decode_responses=True)

            self.cline = redis.Redis(connection_pool=pool)
            logging.info('redis connected...')
            # print('redis connected...')
        except Exception as e:
            print(e)

    def getkey(self, keyname, tojson=1):
        ''' 读取键值
        tojson：是否反序列化
        '''
        try:
            keyname = f"{self.dat_table}:{keyname}"
            value = self.cline.get(keyname)
            if value is None: return None
            try:
                ret = json.loads(value)
            except Exception as e:
                ret = value
            return ret
        except Exception as e:
            print(e)
            return None

    def setkey(self, keyname, dat, ttl=0):
        ''' 设置键值
        '''
        try:
            keyname = f"{self.dat_table}:{keyname}"
            if type(dat) in [tuple, list, dict]:
                try:
                    value = json.dumps(dat)
                except Exception as e:
                    value = dat
            else:
                value = dat
            if ttl <= 0:
                # 永久保存
                self.cline.set(keyname, value)
            else:
                # 按TTL自动超时方式保存
                self.cline.setex(keyname, ttl, value)

            return True
        except Exception as e:
            print(e)
            return False

    def delkey(self, keyname):
        ''' 删除键
        '''
        try:
            keyname = f"{self.dat_table}:{keyname}"
            self.cline.delete(keyname)
            return True
        except Exception as e:
            print(e)
            return False

    def cache(self, keyname, get_data_fun=None, tojson=1, ttl=None):
        ''' 读取缓存，未命中时调用 get_data_fun 方法获得数据
        ttl： 缓存时长，单位：秒，默认使用初始时的配置
        tojson: 是否反序列
        '''
        if ttl is None: ttl = self.ttl

        # print('in cache method...')
        # 读redis缓存
        ret = self.getkey(keyname, tojson=tojson)
        if not ret is None:
            # 命中则直接返回
            print(f'hits cache key:{keyname}...')
            return ret
        else:
            print(f'not hits cache, key={keyname}...')
            # 调用自定义的取值函数
            if get_data_fun is None:
                return None
            else:
                ndat = get_data_fun()
                if ndat:
                    self.setkey(keyname, ndat, ttl=ttl)
                    print(f'svae cache key={keyname}')
                    logging.debug(f'save cache key={keyname}')
                else:
                    logging.debug(f'value empty, cache key:{keyname}')
                return ndat

# 使用示例
def test_rediscache(del_key=0):
    ''' 单元测试
    '''
    import time

    host='192.168.15.111'
    host='localhost'
    host='127.0.0.1'
    port = 6379

    print(f'正在连接Redis:{host}...')
    rc = RedisCache(host=host, port=port)

    def get_value(a, b, c):
        print('in get_value method...')
        #ret = a*b+c
        #ret = '%s_%s_%s' % (a,b,c)
        #ret = (a,b,c)
        #ret = dict(zip('abc', (a,b,c)))

        # 测试key带中文的情况
        ret = dict(zip('老司机', (a, b, c+int(time.time()))))
        return ret


    a,b,c = 2, 3, 4 #int(time.time())
    keyname = '%s_%s_%s' % (a,b,c)
    print(f'keyname:{keyname}...')
    print('a,b,c:', (a,b,c))

    # 使用下面这句是错误的，会直接先去调用get_value
    # ret = rc.cache(keyname, get_value(a,b,c))

    # 正确的方式是先构造一个lambda函数，再传递
    tfun = lambda: get_value(a,b,c)

    # 自动缓存
    print('正在读取缓存...')

    ret = rc.cache(keyname, tfun, tojson=1)
    print('result:', ret)
    print('-'*40)

    # 再读一次，肯定是命中缓存
    print('再读一次缓存...')
    ret = rc.cache(keyname, tfun, tojson=1)
    print('result:', ret)

    # 删除缓存，如果删除那么每次运行 首先是未命中，然后再命中；
    # rand_key = int(time.time()) % 2
    if del_key:
        print('正在删除缓存...')
        rc.delkey(keyname)

if __name__ == '__main__':
    pass
    import fire
    fire.Fire()
