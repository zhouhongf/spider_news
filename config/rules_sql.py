#!/usr/bin/env python
from collections import namedtuple
from urllib.parse import urlencode, urlparse, urljoin, quote, unquote
from myspiders.base import BaseField, Bs4TextField, Bs4HtmlField, Bs4AttrField, Bs4AttrTextField, JsonField, JsonMultiField, JsonDictMultiField
import re
import time
from config.targetsql import TargetSQL


# type_main格式规定为2个中文字
# type_next格式规定为4个中文字
# 新闻，公告，业务，活动
# 新闻：来源本行，来源媒体
# 公告：采购公告，招聘公告，服务公告，其他公告
class RulesSQL:
    pattern_string = re.compile(r'^((?!(【详情】|【详细】|更多)).)*$')
    pattern_date = re.compile(r'20[0-9]{2}[-年/][01]?[0-9][-月/][0123]?[0-9]日?')

    RULES = {
        TargetSQL(
            project_name='手机银行浏览记录分析',
            tables_in=['table_one', 'table_two', 'table_three'],
            table_out='table_out_name',
            sql='select * from %s',
            del_table=True,
            out_many=True,
            method='CREATE',
        )
    }

