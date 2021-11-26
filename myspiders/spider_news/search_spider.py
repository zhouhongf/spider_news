from myspiders.base import Spider
from config import Rules, Target, Paper, Config
from urllib.parse import urlencode, urlparse, urljoin, quote, unquote
from myspiders.base import BaseField, Bs4TextField, Bs4HtmlField, Bs4AttrField, Bs4AttrTextField, JsonField
from bs4 import BeautifulSoup
import re
import os
import async_timeout
from myspiders.base.tools import get_random_user_agent


# 还未完成
class SearchSpider(Spider):
    name = 'SearchSpider'
    pattern_url = re.compile(r'(http://|https://)?([-\w]+\.)+[-\w]+(/[-\w./?%&=]*)?')

    # 通过构造函数，注入start_urls集合，开启自定义蜘蛛启动入口
    async def manual_start_urls(self):
        list_target = []
        if self.start_urls:
            for one in self.start_urls:
                word = one['word']
                page_index = one['page_index']
                if not word.startswith('http://') and not word.startswith('https://'):
                    target = Target(
                        bank_name='BING搜索',
                        type_main='搜索',
                        type_next='文字搜索',
                        url=Config.URL_BING % (quote(word)),
                        selectors=[
                            Bs4HtmlField(css_select='#b_results li.b_algo'),
                            Bs4AttrTextField(target='href', css_select='h2 a', many=False),
                        ]
                    )
                    list_target.append(target)

        for target in list_target:
            headers = {'user-agent': await get_random_user_agent(), 'referer': 'https://cn.bing.com/'}
            cookie = '_EDGE_V=1; MUID=0BA46811B17E6BB63823666DB0506A5A; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=4CB6FD415F384E67ABA5148E11860087&dmnchg=1; MUIDB=0BA46811B17E6BB63823666DB0506A5A; ABDEF=V=0&ABDV=0&MRNB=1582774526576&MRB=0; _SS=SID=0CB60EDE3CD3689C1AE900A03DFD696E&bIm=588; _EDGE_S=mkt=zh-cn&SID=0CB60EDE3CD3689C1AE900A03DFD696E; SRCHUSR=DOB=20200226&T=1582899956000; ipv6=hit=1582903558279&t=6; SNRHOP=I=&TS=; SRCHHPGUSR=CW=981&CH=920&DPR=1&UTC=480&WTS=63718496756&HV=1582900908'
            headers.update({'cookie': cookie})
            async with async_timeout.timeout(2):
                yield self.request(url=target.url, headers=headers, callback=self.parse, metadata={'target': target})

    async def parse(self, response):
        html = await response.text()
        target: Target = response.metadata['target']
        bank_name = target.bank_name
        if bank_name == 'BING搜索':
            selector_one = target.selectors[0]
            selector_two = target.selectors[1]
            list_li = selector_one.extract(soup=html)
            if list_li:
                for li in list_li:
                    text_li = li.get_text()

                    text_a = selector_two.extract(soup=li)
                    title = text_a['text']
                    url = text_a['attr']
                    pattern = re.compile(title + '(.+)' + unquote(url))

                    result = pattern.search(text_li)
                    if result:
                        description = result.group(1)
                        data = {'title': title, 'url': url, 'description': description}
                        print(data)


def start():
    start_urls = [
        {'word': '布什', 'page_index': 1},
        {'word': '水浒', 'page_index': 1},
    ]
    # SearchSpider.start(start_urls=start_urls)
