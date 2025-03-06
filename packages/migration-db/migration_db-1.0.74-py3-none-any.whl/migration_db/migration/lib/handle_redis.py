"""
Author: xiaodong.li
Date: 2020-09-10 12:51:15
LastEditors: xiaodong.li
LastEditTime: 2020-09-23 15:43:30
Description: file content
"""

import redis

from common_utils.log import Logger


def connect_redis(db, host, port, password):
    pool = redis.ConnectionPool(host=host, port=port, db=db, password=password, socket_connect_timeout=5)
    conn = redis.Redis(connection_pool=pool)
    try:
        conn.ping()
    except TimeoutError:
        raise Exception('Redis connection timeout.')
    return conn


def delete_all_key(db, pattern, host, port, password):
    if db not in list(range(6)):
        return
    conn = connect_redis(db, host, port, password)
    keys = conn.keys(f"*{pattern}*")
    if not keys:
        Logger().info(f"DB({db}) is empty!")
        return
    Logger().info(keys[:10])
    deleted_count = conn.delete(*keys)
    Logger().info(f"Delete {deleted_count} redis keys.")
