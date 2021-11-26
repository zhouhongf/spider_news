#!/usr/bin/env python
from collections import namedtuple
from urllib.parse import urlencode, urlparse, urljoin, quote, unquote
from myspiders.base import BaseField, Bs4TextField, Bs4HtmlField, Bs4AttrField, Bs4AttrTextField, JsonField, JsonMultiField, JsonDictMultiField
import re
import time
from config.target import Target


# type_main格式规定为2个中文字
# type_next格式规定为4个中文字
# 新闻，公告，业务，活动
# 新闻：来源本行，来源媒体
# 公告：采购公告，招聘公告，服务公告，其他公告
class RulesHR:
    pattern_string = re.compile(r'^((?!(【详情】|【详细】|更多)).)*$')
    pattern_date = re.compile(r'20[0-9]{2}[-年/][01]?[0-9][-月/][0123]?[0-9]日?')

    RULES = {
        Target(
            bank_name='中国银行',
            type_main='公告',
            type_next='招聘公告',
            url='https://www.boc.cn/aboutboc/bi4/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.news ul.list li a'),
                Bs4HtmlField(css_select='.content.con_area .sub_con', many=False)
            ]
        ),
        Target(
            bank_name='建设银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://job.ccb.com/tran/WCCMainPlatV5?CCB_IBSVersion=V5&isAjaxRequest=true&SERVLET_NAME=WCCMainPlatV5&TXCODE=NHR105&planType=&isImpAnno=1&orgId=&isHomePageDisplay=1&REC_IN_PAGE=15&PAGE_JUMP=1',
            selectors=[
                JsonField(json_select='annoList'),
                JsonDictMultiField(
                    json_select='annoId=url,annoTitle=title,annoDate=date',
                    url_prefix='http://job.ccb.com/tran/WCCMainPlatV5?CCB_IBSVersion=V5&isAjaxRequest=true&SERVLET_NAME=WCCMainPlatV5&TXCODE=NHR106&annoId='
                ),
                JsonField(json_select='annoContent')
            ]
        ),
        Target(
            bank_name='邮储银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://www.psbc.com/cn/index/rczp/rczygg/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#article_1 li.clearfix a'),
                Bs4HtmlField(attrs={'class': 'news_cont_msg'}, many=False)
            ]
        ),
        Target(
            bank_name='中信银行',
            type_main='公告',
            type_next='招聘公告',
            url='https://www.hotjob.cn/wt/chinaciticbank/web/index/aboutUs?columnId=100301',
            selectors=[
                Bs4AttrTextField(target='onclick', css_select='.main_right div div.ant-table-body table tbody tr'),
                Bs4HtmlField(css_select='div.main_right', many=False)
            ]
        ),

        Target(
            bank_name='招商银行',
            type_main='公告',
            type_next='校园招聘',
            url='http://career.cloud.cmbchina.com/api/Notice/GetNoticeList',
            method='POST',
            formdata={"pageSize": 6, "pageIndex": 1, "searchWords": ""},
            selectors=[
                JsonField(json_select='Result'),
                JsonDictMultiField(
                    json_select='NoticeID=url,Title=title,RowUpdatedStr=date',
                    url_prefix='http://career.cloud.cmbchina.com/api/Notice/GetNoticeDetailInfo?noticeID='
                ),
                JsonField(json_select='Result>Contents'),
            ]
        ),
        Target(
            bank_name='招商银行',
            type_main='公告',
            type_next='社会招聘',
            url='http://career.cmbchina.com/api/Notice/GetNoticeList',
            method='POST',
            formdata={"pageSize": 6, "pageIndex": 1, "searchWords": ""},
            selectors=[
                JsonField(json_select='Result'),
                JsonDictMultiField(
                    json_select='NoticeID=url,Title=title,RowUpdatedStr=date',
                    url_prefix='http://career.cmbchina.com/api/Notice/GetNoticeDetailInfo?noticeID='
                ),
                JsonField(json_select='Result>Contents'),
            ]
        ),
        Target(
            bank_name='民生银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://career.cmbc.com.cn:8080/portal/rest/notice/search.view?random=%s' % int(time.time() * 1000),
            method='POST',
            formdata={'view': 'noticeList', 'pageNo': 1, 'pageSize': 20, 'searchNotRecruitTypeId': 'internal'},
            selectors=[
                JsonField(json_select='data>items'),
                JsonDictMultiField(
                    json_select='id=url,name=title,publishTime=date',
                    url_prefix='http://career.cmbc.com.cn:8080/portal/rest/notice/view.view?random=%s&view=noticeView&id=' % int(time.time() * 1000),
                ),
                JsonField(json_select='data>detailContent'),
            ]
        ),
        Target(
            bank_name='兴业银行',
            type_main='公告',
            type_next='招聘公告',
            url='https://www.cib.com.cn/cn/aboutCIB/about/jobs/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.list-box .middle ul li a'),
                Bs4HtmlField(css_select='#content .detail-box div.middle', many=False)
            ]
        ),
        Target(
            bank_name='华夏银行',
            type_main='公告',
            type_next='招聘公告',
            url='https://zhaopin.hxb.com.cn/zpWeb/zpweb/qsList.do',
            selectors=[
                Bs4AttrTextField(target='href', name='a',
                                 attrs={'href': re.compile(r'/zpWeb/zpweb/bulletinEdit.do\?')}),
                Bs4HtmlField(css_select='.root_div table:nth-of-type(2) tr td table:nth-of-type(2)', many=False)
            ]
        ),

        Target(
            bank_name='恒丰银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://career.hfbank.com.cn/ucms/AnnouncementServlet',
            method='POST',
            formdata={
                'SiteId': '312',
                'gopage': '1',
                'ggjg': '',
                'ggzplb': '',
                'col': 'title|link|PublishDate|Keyword|Summary|ggzplb|ggzpjg',
                'search': '',
                'CatalogID': '11185'
            },
            selectors=[
                JsonField(json_select='rows'),
                JsonDictMultiField(json_select='link=url,title=title,PublishDate=date',
                                   url_prefix='http://career.hfbank.com.cn/'),
                Bs4HtmlField(css_select='.bg_grey .ggxx_contain', many=False),
            ]
        ),

        Target(
            bank_name='杭州银行',
            type_main='公告',
            type_next='招聘公告',
            url='https://myjob.hzbank.com.cn/hzzp-apply/service/systemNotice/show?page=0&size=10',
            selectors=[
                JsonField(json_select='content'),
                JsonDictMultiField(
                    json_select='id=url,title=title,publishTime=date',
                    url_prefix='https://myjob.hzbank.com.cn/hzzp-apply/service/systemNotice/'
                ),
                JsonField(json_select='content'),
            ]
        ),

        Target(
            bank_name='江苏银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://www.jsbchina.cn/CN/gywh/grczp/rrczp/index.html?flag=1',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#myTab0_Content ul a[href^="/CN/gywh/"]',
                    url_prefix='http://www.jsbchina.cn/'),
                Bs4HtmlField(css_select='#myTab0_Content0', many=False)
            ]
        ),

        Target(
            bank_name='南京银行',
            type_main='公告',
            type_next='招聘公告',
            url='https://job.njcb.com.cn/recruit/api/index/getNoticContent',
            method='POST',
            formdata={'typeName': 'notic'},
            selectors=[
                JsonField(json_select='obj>noticVoList'),
                JsonDictMultiField(json_select='id=url,title=title,addTime=date,content=content')
            ]
        ),
        Target(
            bank_name='南京银行',
            type_main='公告',
            type_next='招聘公告',
            url='https://job.njcb.com.cn/recruit/api/index/getNoticContent',
            method='POST',
            formdata={'typeName': 'long'},
            selectors=[
                JsonField(json_select='obj>noticVoList'),
                JsonDictMultiField(json_select='id=url,title=title,addTime=date,content=content')
            ]
        ),
        Target(
            bank_name='南京银行',
            type_main='公告',
            type_next='招聘公告',
            url='https://job.njcb.com.cn/recruit/api/index/getNoticContent',
            method='POST',
            formdata={'typeName': 'short'},
            selectors=[
                JsonField(json_select='obj>noticVoList'),
                JsonDictMultiField(json_select='id=url,title=title,addTime=date,content=content')
            ]
        ),
        Target(
            bank_name='青岛银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://www.qdccb.com/rlzy/shzp/index.shtml',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='.tableList tr td:nth-of-type(2) a[href^="/rlzy/shzp/"]',
                    url_prefix='http://www.qdccb.com/'),
                Bs4HtmlField(css_select='.main .second_right .second_rightContent', many=False)
            ]
        ),

        Target(
            bank_name='苏州银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://hr.suzhoubank.com/zpWeb/zpweb/qsList.do',
            selectors=[
                Bs4AttrTextField(target='href', name='a',
                                 attrs={'href': re.compile(r'/zpWeb/zpweb/bulletinEdit\.do\?')}),
                Bs4HtmlField(css_select='table tr td table:nth-of-type(2)', many=False)
            ]
        ),
        Target(
            bank_name='西安银行',
            type_main='公告',
            type_next='招聘公告',
            url='https://job.xacbank.com:8001/client/viewnotices/retrieval_noticelist.htm?noticetitle=&channel=all',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='.main_box .recent .recent_box .table_box .com_table table tbody tr td.trs a',
                                 url_prefix='https://job.xacbank.com:8001'),
                Bs4HtmlField(css_select='.layui-form-item.layui-form-text', many=False)
            ]
        ),

        Target(
            bank_name='长沙银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://bcs.hotjob.cn/wt/BCS/web/index/aboutUs?columnId=100702',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='.enter_main .main_left ul ul li a',
                                 url_prefix='http://bcs.hotjob.cn'),
                Bs4HtmlField(css_select='.enter_main .main_right', many=False)
            ]
        ),
        Target(
            bank_name='常熟银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://www.csrcbank.com/tb/rczp/zxzp_358/',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='ul#data li a',
                                 url_prefix='http://www.csrcbank.com/tb/rczp/zxzp_358/'),
                Bs4HtmlField(css_select='#tabstyle .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='江阴银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://www.jybank.com.cn/eportal/ui?pageId=373464',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='#text .recruitment-con ul li a',
                                 url_prefix='http://www.jybank.com.cn/eportal/ui'),
                Bs4HtmlField(css_select='#text .portlet div:nth-of-type(2) div.pre0', many=False)
            ]
        ),
        Target(
            bank_name='青农银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://www.qrcb.com.cn/qrcbcms/html/khfw/20190505/1071.html',
            selectors=[
                Bs4TextField(css_select='.main_right .box5 .zhengwen_con1 div p'),
                Bs4HtmlField(css_select='.main .main_right .box5 .zhengwen_con1', many=False)
            ]
        ),
        Target(
            bank_name='苏农银行',
            type_main='公告',
            type_next='招聘公告',
            url='http://www.szrcb.com/wjrcb/kjcd/ymbj/dbkjcd/rczp/?v=%s' % int(time.time() * 1000),
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='ul li a[href^="/wjrcb/kjcd/ymbj/"]',
                                 url_prefix='http://www.szrcb.com/'),
                Bs4HtmlField(css_select='.bg-ff .main-lc .lccpbox .lbright .ggpad', many=False)
            ]
        ),
        Target(
            bank_name='紫金银行',
            type_main='公告',
            type_next='招聘公告',
            url='https://hr1.zjrcbank.com/app/api/v1/job/notice?category=0&pageNumber=1',
            headers={'Referer': 'https://hr1.zjrcbank.com/'},
            selectors=[
                JsonField(json_select='data>rows'),
                JsonDictMultiField(json_select='rowId=url,title=title,publishTime=date'),
                JsonField(json_select='data>JobRecruitNoticeBean>content')
            ]
        ),
    }

