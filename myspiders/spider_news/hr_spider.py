from myspiders.base import Spider, Response, MainContent, JsonField
from myspiders.base.tools import fetch_by_splash
from config import RulesHR, Target, Paper
from urllib.parse import urlencode, urlparse, urljoin, quote, unquote
from bs4 import BeautifulSoup
import re
import os
import farmhash
from utils.time_util import day_standard, daytime_standard
import json
import time


class HrSpider(Spider):
    name = 'HrSpider'
    targets = RulesHR.RULES
    suffix_file = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.zip', '.rar', '.tar', '.bz2', '.7z', '.gz']

    async def parse(self, response):
        target: Target = response.metadata['target']
        bank_name = target.bank_name
        selector = target.selectors[0]
        callback = selector.callback
        if callback:
            parse_method = getattr(self, callback, None)
        else:
            parse_method = getattr(self, 'parse_rows', None)
        if parse_method is not None and callable(parse_method):
            yield parse_method(response, target)
        else:
            self.logger.error('【%s】没有找到相应的方法：parse_方法' % bank_name)

    async def parse_rows(self, response: Response, target: Target):
        bank_name = target.bank_name
        selector = target.selectors[0]
        if type(selector) == JsonField:
            list_need = await self.get_list_by_json(bank_name=bank_name, selectors=target.selectors, response=response)
        else:
            list_need = await self.get_list_by_html(bank_name=bank_name, selector=selector, response=response)
        print('list_need准备获取：', list_need)
        yield self.request_content(list_need=list_need, response=response, target=target)

    async def request_content(self, list_need: list, response: Response, target: Target):
        url_old = response.url
        domain = urlparse(url_old).netloc
        for one in list_need:
            title = one['title']
            url_next = one['url']
            issue_date = one['date']

            id_hash = str(farmhash.hash64(url_next))
            one_exit = self.collection.find({'$or': [{'_id': {'$eq': id_hash}}, {'name': {'$eq': title}}]})
            if one_exit.count() == 0:
                if target.bank_name == '南京银行':
                    paper = Paper(
                        bank_name=target.bank_name,
                        type_main=target.type_main,
                        type_next=target.type_next,
                        name=title,
                        url=url_next,
                        date=issue_date,
                        content=one['content']
                    )
                    print('准备保存：', paper)
                    await self.save_paper(paper)
                else:
                    paper = Paper(bank_name=target.bank_name, type_main=target.type_main, type_next=target.type_next, name=title, url=url_next, date=issue_date)
                    metadata = {'selector': target.selectors[-1], 'paper': paper}
                    selector_last = target.selectors[-1]
                    if type(selector_last) == JsonField:
                        callback = self.parse_content_by_json
                    else:
                        callback = self.parse_content_by_html

                    # 排除文件类型的链接，和不是同一个域名的链接
                    url_suffix = os.path.splitext(url_next)[-1]
                    domain_next = urlparse(url_next).netloc
                    query_path = urlparse(url_next).path
                    if url_suffix not in self.suffix_file and query_path:
                        print('准备请求详情内容：', url_next)
                        if target.bank_name == '苏州银行':
                            yield self.fetch_by_splash(url_next=url_next, paper=paper, target=target)
                        elif target.bank_name == '紫金银行':
                            self.headers['Referer'] = 'https://hr1.zjrcbank.com/index/' + url_next
                            url_next = 'https://hr1.zjrcbank.com/app/api/v1/job/notice/' + url_next
                            yield self.handle_request(self.request(url=url_next, headers=self.headers, callback=callback, metadata=metadata))
                        else:
                            yield self.handle_request(self.request(url=url_next, callback=callback, metadata=metadata))  # 使用handle_requests防止一次性过多的访问

    async def get_list_by_json(self, bank_name: str, selectors: list, response: Response):
        list_need = []
        try:
            data = await response.json()
        except:
            try:
                data = await response.json(content_type='text/html')
            except:
                data = await response.json(content_type='text/xml')

        selector_one = selectors[0]
        data_need = selector_one.extract(jsondata=data)
        if type(data_need) == list:
            list_need = data_need
        else:
            list_need.append(data_need)

        if len(selectors) == 1:
            return list_need

        list_need_extra = []
        selector_two = selectors[1]
        for one in list_need:
            one_need = selector_two.extract(jsondata=one)
            date = one_need['date']
            if bank_name == '杭州银行':
                one_need['date'] = date[0:4] + '-' + date[4:6] + '-' + date[6:8] + ' 00:00:00'
            else:
                one_need['date'] = daytime_standard(date)
            list_need_extra.append(one_need)
        return list_need_extra

    async def get_list_by_html(self, bank_name, selector, response):
        list_need = []
        url_old = response.url
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        # text是整个列表页面的文字，将括号，书名号等去掉
        text = re.sub(r'[【】\[\]()（）\s|]+', '', soup.get_text(strip=True))
        list_chapter = selector.extract(soup=html)
        if bank_name == '青农银行':
            for one in list_chapter:
                if one:
                    list_one = one.split('：')
                    url_next = list_one[1]
                    res = re.compile(r'\d{8}').search(url_next)
                    issue_date = ''
                    if res:
                        date = res.group()
                        issue_date = date[0:4] + '-' + date[4:6] + '-' + date[6:8] + ' 00:00:00'
                    data_need = {'title': list_one[0], 'url': list_one[1], 'date': issue_date}
                    list_need.append(data_need)
            return list_need

        for one in list_chapter:
            title = re.sub(r'[【】\[\]()（）\s|]+', '', one['text'])

            if bank_name == '中信银行':
                attr = one['attr']
                res = re.compile(self.pattern_link).search(attr)
                if res:
                    url_next = res.group()
                else:
                    url_next = ''
            else:
                url_next = one['attr']
                if not url_next.startswith('http'):
                    url_next = urljoin(url_old, url_next)

            issue_date = None
            if bank_name in ['平安银行', '浙商银行', '交通银行', '贵阳银行', '江苏银行', '郑州银行', '中信银行']:
                # 正则匹配 寻找标题中的日期
                pattern_date = re.compile(self.pattern_date).findall(title)
                if pattern_date:
                    if bank_name == '平安银行':
                        issue_date = pattern_date[0]
                    else:
                        issue_date = pattern_date[-1]
                    title = title.replace(issue_date, '')
            elif bank_name == '上海银行':
                pattern_date = re.compile(r'\d{8}').search(title)
                if pattern_date:
                    date = pattern_date.group()
                    title = title.replace(date, '')
                    issue_date = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
            elif bank_name in ['华夏银行', '苏州银行']:
                pattern_date = re.compile(title + '[new]{0,3}(' + self.pattern_date + ')').search(text)
                if pattern_date:
                    issue_date = pattern_date.group(1)
            elif bank_name in ['广发银行', '南京银行', '紫金银行']:
                # 正则匹配 寻找整个页面中的日期，格式一，加括号，是用于提取日期
                pattern_date = re.compile('(' + self.pattern_date + ')' + title).search(text)
                if pattern_date:
                    issue_date = pattern_date.group(1)
            elif bank_name in ['宁波银行']:
                pattern_date = re.compile(title + '(' + self.pattern_date_extra + ')').search(text)
                if pattern_date:
                    issue_date = pattern_date.group(1)
            else:
                # 正则匹配 寻找整个页面中的日期，格式二，加括号，是用于提取日期
                pattern_date = re.compile(title + '(' + self.pattern_date + ')').search(text)
                if pattern_date:
                    issue_date = pattern_date.group(1)
            # 将日期转换为标准格式
            if issue_date:
                issue_date = daytime_standard(issue_date)

            data_need = {'title': title, 'url': url_next, 'date': issue_date}
            list_need.append(data_need)
        return list_need

    async def parse_content_by_json(self, response):
        paper: Paper = response.metadata['paper']
        selector = response.metadata['selector']
        try:
            data = await response.json()
        except:
            try:
                data = await response.json(content_type='text/html')
            except:
                data = await response.json(content_type='text/xml')
        content = selector.extract(jsondata=data)
        paper.content = content
        print('准备保存：', paper)
        await self.save_paper(paper)

    async def parse_content_by_html(self, response):
        paper: Paper = response.metadata['paper']
        selector = response.metadata['selector']
        html = await response.text()
        tag = selector.extract(soup=html)
        if tag:
            html_need = tag.prettify()
        else:
            html_need = html
        if paper.bank_name == '青农银行':
            content = tag.get_text()
            paper.content = content
            print('准备保存：', paper)
            await self.save_paper(paper)
        else:
            await self.parse_maincontent(html=html_need, paper=paper)

    async def fetch_by_splash(self, url_next: str, paper: Paper, target: Target):
        jsondata = await fetch_by_splash(link=url_next)
        html = jsondata['html']
        selector = target.selectors[-1]
        tag = selector.extract(soup=html)
        if tag:
            html_need = tag.prettify()
        else:
            html_need = html
        await self.parse_maincontent(html=html_need, paper=paper)

    async def parse_maincontent(self, html: str, paper: Paper):
        mc = MainContent()
        title, content = mc.extract(url='', html=html)
        # 如果content中的数字数量多于中文文字的数量，则不放入数据库中
        chinese = re.compile(self.pattern_chinese).findall(content)
        numbers = re.compile(self.pattern_number).findall(content)
        if len(content) > 100 and len(chinese) > len(numbers):
            paper.content = content
            # 如果在前面列表页上没有找到发布日期，则在正文中查找
            if not paper.date:
                list_date = re.compile(self.pattern_date).findall(content)
                if list_date:
                    date_first = day_standard(list_date[0])
                    date_last = day_standard(list_date[-1])
                    date_first = daytime_standard(date_first)
                    date_last = daytime_standard(date_last)
                    paper.date = max(date_first, date_last)

            print('准备保存：', paper)
            await self.save_paper(paper)


def start():
    HrSpider.start()
    # pass







