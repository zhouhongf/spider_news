from myspiders.base import Spider, Response, MainContent, JsonField, Bs4AttrField, Bs4HtmlField, Bs4TextField, Bs4AttrTextField
from myspiders.base.tools import fetch_by_splash
from config import Target, Paper, BankDict
from urllib.parse import urlencode, urlparse, urljoin, quote, unquote
from bs4 import BeautifulSoup
import re
import os
import farmhash
from utils.time_util import day_standard, daytime_standard
import json
import time


class BankworkSpider(Spider):

    async def parse(self, response):
        target: Target = response.metadata['target']
        selectors = target.selectors
        if len(selectors) == 1:
            yield self.parse_content(response, target)
        else:
            selector = selectors[0]
            callback = selector.callback
            if callback:
                parse_method = getattr(self, callback, None)
            else:
                parse_method = getattr(self, 'parse_rows', None)
            if parse_method is not None and callable(parse_method):
                yield parse_method(response, target)
            else:
                self.logger.error('【%s】没有找到相应的方法：parse_方法' % target.bank_name)

    async def parse_content(self, response: Response, target: Target):
        url_old = target.url
        id_hash = str(farmhash.hash64(url_old))
        one_exit = self.collection.find({'_id': id_hash})
        if one_exit.count() == 0:
            paper = Paper(
                bank_name=target.bank_name,
                type_main=target.type_main,
                type_next=target.type_next,
                type_one=target.type_one,
                type_two=target.type_two,
                type_three=target.type_three,
                name='',
                url=url_old
            )

            selector = target.selectors[0]
            if type(selector) != JsonField:
                if type(selector) == Bs4AttrField and selector.target in ['src']:
                    print('========================== 下载图片 ========================= ')
                    await self.save_content_with_file(response=response, selector=selector, paper=paper)
                else:
                    html = await response.text()
                    tag = selector.extract(soup=html)
                    html_need = tag.prettify()

                    cssdata = selector.cssdata
                    metadata = selector.metadata
                    if 'name' in cssdata.keys():
                        name_css_select = cssdata['name']
                        name_dom = tag.select_one(name_css_select)
                        paper.name = name_dom.get_text(strip=True)
                    elif 'name' in metadata.keys():
                        paper.name = metadata['name']
                    if 'content' in cssdata.keys():
                        content_css_select = cssdata['content']
                        html_need = tag.select_one(content_css_select)
                        html_need = html_need.prettify()

                    if paper.name not in ['品牌介绍', '所获奖项', '业务综述', '流程图', '荣誉榜']:
                        if '立即申请' in paper.name:
                            name = paper.name
                            paper.name = name.replace('立即申请', '')
                        await self.parse_maincontent(html=html_need, paper=paper)

    async def parse_rows(self, response: Response, target: Target):
        bank_name = target.bank_name
        selectors = target.selectors
        selector = selectors[0]
        if type(selector) == JsonField:
            list_need = await self.get_list_by_json(bank_name=bank_name, selectors=selectors, response=response)
        else:
            list_need = await self.get_list_by_html(bank_name=bank_name, selectors=selectors, response=response)
        yield self.request_content(list_need=list_need, response=response, target=target)

    async def request_content(self, list_need: list, response: Response, target: Target):
        url_old = response.url
        domain = urlparse(url_old).netloc
        for one in list_need:
            title = one['title']
            url_next = one['url']
            if not url_next.startswith('http'):
                url_next = urljoin(url_old, url_next)

            id_hash = str(farmhash.hash64(url_next))
            one_exit = self.collection.find({'$or': [{'_id': {'$eq': id_hash}}, {'name': {'$eq': title}}]})
            if one_exit.count() == 0:
                paper = Paper(
                    bank_name=target.bank_name,
                    type_main=target.type_main,
                    type_next=target.type_next,
                    type_one=target.type_one,
                    type_two=target.type_two,
                    type_three=target.type_three,
                    name=title,
                    url=url_next
                )
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
                    yield self.handle_request(self.request(url=url_next, callback=callback, metadata=metadata))

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
            one_need['date'] = daytime_standard(date)
            list_need_extra.append(one_need)
        return list_need_extra

    async def get_list_by_html(self, bank_name: str, selectors: list, response: Response):
        list_need = []
        html = await response.text()
        selector_one = selectors[0]
        list_data = selector_one.extract(soup=html)
        if type(selector_one) == Bs4AttrTextField:
            for one in list_data:
                title = one['text']
                url_next = one['attr']
                if title:
                    title = re.sub(r'[【】\[\]()（）\s|]+', '', title)
                data_need = {'title': title, 'url': url_next}
                list_need.append(data_need)
        else:
            for one in list_data:
                data_need = {'title': '', 'url': one}
                list_need.append(data_need)

        if len(selectors) == 2:
            return list_need

        list_need_extra = []
        selector_two = selectors[1]
        for one in list_need:
            url_dom = one['url']
            one_need = selector_two.extract(soup=url_dom)
            data_need = {'title': one_need['text'], 'url': one_need['attr']}
            list_need_extra.append(data_need)
        return list_need_extra


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
        if paper.name not in ['品牌介绍', '所获奖项', '业务综述', '流程图', '荣誉榜']:
            print('准备保存：', paper)
            await self.save_paper(paper)

    async def parse_content_by_html(self, response):
        paper: Paper = response.metadata['paper']
        selector = response.metadata['selector']
        html = await response.text()
        tag = selector.extract(soup=html)
        if not paper.name:
            cssdata = selector.cssdata
            metadata = selector.metadata
            if 'name' in cssdata.keys():
                name_css_select = cssdata['name']
                name_dom = tag.select_one(name_css_select)
                paper.name = name_dom.get_text(strip=True)
            elif 'name' in metadata.keys():
                paper.name = metadata['name']

        if tag:
            html_need = tag.prettify()
        else:
            html_need = html
        await self.parse_maincontent(html=html_need, paper=paper)

    async def fetch_by_splash_parse(self, url_next: str, paper: Paper, target: Target):
        jsondata = await fetch_by_splash(link=url_next)
        html = jsondata['html']
        selector = target.selectors[-1]
        tag = selector.extract(soup=html)
        if tag:
            html_need = tag.prettify()
        else:
            html_need = html
        await self.parse_maincontent(html=html_need, paper=paper)

    async def save_content_with_file(self, response: Response, selector: Bs4AttrField, paper: Paper):
        url_old = response.url
        html = await response.text()
        tag = selector.extract(soup=html)
        if type(tag) == dict and 'attr' in tag.keys():
            url_file = tag['attr']
            if not url_file.startswith('http'):
                url_file = urljoin(url_old, url_file)
            data_file = await self.download_save_document(bank_name=paper.bank_name, url=url_file, file_type=BankDict.file_type['photo_bankwork'])
            paper.name = tag['name']
            paper.content = tag['content']
            paper.photos = data_file['_id']
            paper.url = url_file
            if paper.name not in ['品牌介绍', '所获奖项', '业务综述', '流程图', '荣誉榜']:
                print('准备保存：', paper)
                await self.save_paper(paper)

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

            if paper.name not in ['品牌介绍', '所获奖项', '业务综述', '流程图', '荣誉榜']:
                print('准备保存：', paper)
                await self.save_paper(paper)


