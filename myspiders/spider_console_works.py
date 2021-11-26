import os
import sys
from config import Config
from importlib import import_module

# sys.path.append('../')


def file_name(file_dir=os.path.join(Config.BASE_DIR, 'myspiders/spider_works')):
    all_files = []
    for file in os.listdir(file_dir):
        if file.endswith('_spider.py'):
            all_files.append(file.replace('.py', ''))
    return all_files


def spider_console_works():
    all_files = file_name()
    for spider in all_files:
        spider_module = import_module("myspiders.spider_works.{}".format(spider))
        spider_module.start()


if __name__ == '__main__':
    spider_console_works()
