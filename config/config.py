import os
import sys


class Config:

    GROUP_NAME = 'ubank'
    PROJECT_NAME = 'spider_news'

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)

    TIMEZONE = 'Asia/Shanghai'
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'

    SCHEDULED_DICT = {
        'time_interval': int(os.getenv('TIME_INTERVAL', 1440)),              # 每24小时定时爬取时间
        'time_long': int(os.getenv('TIME_INTERVAL', 10080)),                 # 每周定时爬取
    }

    HOST_LOCAL = '192.168.3.110'
    HOST_REMOTE = '192.168.3.110'
    MONGO_DICT = {
        'host': HOST_LOCAL,
        'port': 27017,
        'db': GROUP_NAME,
        'username': 'root',
        'password': 'Zhouhf873@',
    }

    URL_BING = "https://cn.bing.com/search?q=%s"
    URL_BAIDU = 'http://www.baidu.com/s'
    URL_SO = "https://www.so.com/s"
    URL_DUCKGO = "https://duckduckgo.com/html"



