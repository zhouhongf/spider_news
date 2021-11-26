from myspiders.base import Spider, Response, MainContent, JsonMultiField
from config import Rules, Target, Paper
from urllib.parse import urlencode, urlparse, urljoin, quote, unquote
from bs4 import BeautifulSoup
import re
import os
import farmhash
from utils.time_util import day_standard, daytime_standard
import json


class TargetSpider(Spider):
    name = 'TargetSpider'
    targets = Rules.RULES
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

    async def parse_zrcbank(self, response: Response, target: Target):
        selectors = target.selectors
        selector = selectors[0]

        html = await response.text()
        url_temp = selector.extract(soup=html)
        pattern = re.compile(r'\'(.+)\'')
        res = pattern.search(url_temp)
        if res:
            url = res.group(1)
            if not url.startswith('http'):
                url = urljoin(response.url, url)
            selectors.pop(0)
            target.selectors = selectors
            yield self.request(url=url, callback=self.parse, metadata={'target': target})

    async def parse_rows(self, response: Response, target: Target):
        print('============== 进入parse_rows方法')
        url_old = response.url
        domain = urlparse(url_old).netloc

        bank_name = target.bank_name
        selector = target.selectors[0]
        if type(selector) == JsonMultiField:
            list_need = await self.get_list_by_json(bank_name=bank_name, selector=selector, response=response)
        else:
            list_need = await self.get_list_by_html(bank_name=bank_name, selector=selector, response=response)

        for one in list_need:
            title = one['title']
            url_next = one['url']
            issue_date = one['date']

            id_hash = str(farmhash.hash64(url_next))
            one_exit = self.collection.find({'$or': [{'_id': {'$eq': id_hash}}, {'name': {'$eq': title}}]})
            if one_exit.count() == 0:
                paper = Paper(bank_name=target.bank_name, type_main=target.type_main, type_next=target.type_next, name=title, url=url_next, date=issue_date)
                metadata = {'selector': target.selectors[-1], 'paper': paper}

                # 排除文件类型的链接，和不是同一个域名的链接
                url_suffix = os.path.splitext(url_next)[-1]
                domain_next = urlparse(url_next).netloc
                if url_suffix not in self.suffix_file and domain_next == domain:
                    print('准备请求详情内容：', url_next)
                    yield self.handle_request(self.request(url=url_next, callback=self.parse_content, metadata=metadata))  # 使用handle_requests防止一次性过多的访问

    async def get_list_by_json(self, bank_name, selector, response):
        list_need = []
        if bank_name in ['苏州银行', '西安银行']:
            text = await response.text()

            text = text.strip()[1:]
            list_text = text.split('\r\n,')
            for one in list_text:
                data = json.loads(one)
                data_need = selector.extract(jsondata=data)

                date = data_need['date']
                data_need['date'] = daytime_standard(date)
                list_need.append(data_need)
            list_need = list_need[-10:]
        return list_need

    async def get_list_by_html(self, bank_name, selector, response):
        list_need = []
        url_old = response.url
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        # text是整个列表页面的文字，将括号，书名号等去掉
        text = re.sub(r'[【】\[\]()（）\s|]+', '', soup.get_text(strip=True))
        list_chapter = selector.extract(soup=html)

        for one in list_chapter:
            title = re.sub(r'[【】\[\]()（）\s|]+', '', one['text'])

            url_next = one['attr']
            if not url_next.startswith('http'):
                url_next = urljoin(url_old, url_next)

            issue_date = None
            if bank_name in ['平安银行', '华夏银行', '浙商银行', '交通银行', '贵阳银行', '江苏银行', '郑州银行']:
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


    async def parse_content(self, response):
        paper: Paper = response.metadata['paper']
        selector = response.metadata['selector']
        html = await response.text()
        if html:
            tag = selector.extract(soup=html)
            if tag:
                html_need = tag.prettify()
            else:
                html_need = html

            mc = MainContent()
            title, content = mc.extract(url='', html=html_need)
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
    TargetSpider.start()
    # pass







