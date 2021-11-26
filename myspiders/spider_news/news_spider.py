from myspiders.base import Spider, MainContent, Bs4AttrTextField
from config import Rules, Target, Paper
from urllib.parse import urlencode, urlparse, urljoin, quote, unquote
from bs4 import BeautifulSoup
import re
import os


class NewsSpider(Spider):
    name = 'NewsSpider'
    targets = Rules.RULES_NEWS

    async def parse(self, response):
        url_old = response.url
        domain = urlparse(url_old).netloc

        html = await response.text()
        target: Target = response.metadata['target']

        chapter_selector = target.selectors[0]
        if isinstance(chapter_selector, Bs4AttrTextField):
            list_chapter = chapter_selector.extract(soup=html)
            for one in list_chapter:
                title = re.sub(r'[【】\[\]()（）\s]+', '', one['text'])
                url_next = one['attr']

                if not url_next.startswith('http'):
                    url_next = urljoin(url_old, url_next)
                # 如果url中带？则表明是带参数的链接，直接跳过，然后继续循环
                position = url_next.find('?')
                if position > -1:
                    url_next = url_next[:position]
                    print('================= 非想要的链接：', url_next)
                    continue

                # 正则匹配 从url_next当中寻找日期
                issue_date = None
                pattern_date = re.compile(self.pattern_date).search(url_next)
                if pattern_date:
                    issue_date = pattern_date.group(0)

                paper = Paper(bank_name=target.bank_name, type_main=target.type_main, type_next=target.type_next, name=title, url=url_next, date=issue_date)
                metadata = {'paper': paper}

                # 排除不是同一个域名的链接
                domain_next = urlparse(url_next).netloc
                if domain_next == domain:
                    print('准备第二次请求：', url_next)
                    yield self.handle_request(self.request(url=url_next, callback=self.parse_next, metadata=metadata))    # 使用handle_requests防止一次性过多的访问

    async def parse_next(self, response):
        paper: Paper = response.metadata['paper']
        html = await response.text()
        if html:
            mc = MainContent()
            title, content = mc.extract(url='', html=html)
            # 如果content中的数字数量多于中文文字的数量，则不放入数据库中
            chinese = re.compile(self.pattern_chinese).findall(content)
            numbers = re.compile(self.pattern_number).findall(content)
            if len(content) > 100 and len(chinese) > len(numbers):
                paper.content = content
                print('准备保存：', paper)
                # print('================ 保存的内容是：', paper.content)
                await self.save_paper(paper)


def start():
    NewsSpider.start()
    # pass






