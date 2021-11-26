#!/usr/bin/env python
from collections import namedtuple
from urllib.parse import urlencode, urlparse, urljoin, quote, unquote
from myspiders.base import BaseField, Bs4TextField, Bs4HtmlField, Bs4AttrField, Bs4AttrTextField, JsonField, JsonMultiField
import re
import time
from config.target import Target

# type_main格式规定为2个中文字
# type_next格式规定为4个中文字
# 新闻，公告，业务，活动
# 新闻：来源本行，来源媒体
# 公告：采购公告，招聘公告，服务公告，其他公告
class Rules:
    pattern_string = re.compile(r'^((?!(【详情】|【详细】|更多)).)*$')
    pattern_date = re.compile(r'20[0-9]{2}[-年/][01]?[0-9][-月/][0123]?[0-9]日?')

    pattern_sina = re.compile(r'https://finance.sina.com.cn/.+/doc-.+\.(shtml|shtm|html|htm)')


    RULES_NEWS = {
        Target(
            bank_name='新浪财经',
            type_main='新闻',
            type_next='首页要闻',
            url='http://finance.sina.com.cn/money/bank/',
            selectors=[
                Bs4AttrTextField(target='href', name='a', attrs={'href': pattern_sina}, string=pattern_string),
            ]
        ),
        Target(
            bank_name='新浪财经',
            type_main='新闻',
            type_next='监管政策',
            url='http://finance.sina.com.cn/roll/index.d.html?cid=56689&page=1',
            selectors=[
                Bs4AttrTextField(target='href', name='a', attrs={'href': pattern_sina}, string=pattern_string),
            ]
        ),
        Target(
            bank_name='新浪财经',
            type_main='新闻',
            type_next='公司动态',
            url='http://finance.sina.com.cn/roll/index.d.html?cid=80798&page=1',
            selectors=[
                Bs4AttrTextField(target='href', name='a', attrs={'href': pattern_sina}, string=pattern_string),
            ]
        ),
        Target(
            bank_name='新浪财经',
            type_main='新闻',
            type_next='产品业务',
            url='http://finance.sina.com.cn/roll/index.d.html?cid=56693&page=1',
            selectors=[
                Bs4AttrTextField(target='href', name='a', attrs={'href': pattern_sina}, string=pattern_string),
            ]
        ),
        Target(
            bank_name='新浪财经',
            type_main='新闻',
            type_next='理财要闻',
            url='http://finance.sina.com.cn/money/',
            selectors=[
                Bs4HtmlField(attrs={'id': re.compile(r'subShowContent1_news[0-9]')}),
                Bs4AttrTextField(target='href', name='a', attrs={'href': pattern_sina}, string=pattern_string),
            ]
        ),
        Target(
            bank_name='新浪财经',
            type_main='新闻',
            type_next='理财要闻',
            url='http://finance.sina.com.cn/money/',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='div[id^="subShowContent1_news"] .news-item h2 a[href*="/doc-"]'),
            ]
        ),
    }

    # 每次仅爬取首页内容
    RULES = {
        Target(
            bank_name='工商银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.icbc.com.cn/icbc/%e5%b7%a5%e8%a1%8c%e9%a3%8e%e8%b2%8c/%e5%b7%a5%e8%a1%8c%e5%bf%ab%e8%ae%af/default.htm',
            selectors=[
                Bs4AttrTextField(target='href', attrs={'class': 'data-collecting-sign textgs'}),
                Bs4HtmlField(attrs={'id': 'MyFreeTemplateUserControl'}, many=False)
            ]
        ),
        Target(
            bank_name='中国银行',
            type_main='新闻',
            type_next='来源本行',
            url='https://www.boc.cn/aboutboc/bi1/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.news ul.list li a'),
                Bs4HtmlField(css_select='.content.con_area .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='中国银行',
            type_main='公告',
            type_next='其他公告',
            url='https://www.boc.cn/custserv/bi2/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.news ul.list li a'),
                Bs4HtmlField(css_select='.content.con_area .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='中国银行',
            type_main='公告',
            type_next='采购公告',
            url='https://www.boc.cn/aboutboc/bi6/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.news ul.list li a'),
                Bs4HtmlField(css_select='.content.con_area .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='农业银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.abchina.com/cn/AboutABC/nonghzx/NewsCenter/default.htm',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.details_rightC.fl a'),
                Bs4HtmlField(css_select='.details_right .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='农业银行',
            type_main='公告',
            type_next='采购公告',
            url='http://www.abchina.com/cn/AboutABC/CG/BM/default.htm',
            selectors=[
                Bs4AttrTextField(target='href', name='a', attrs={'href': re.compile(r'\.htm|\.html')}, string=re.compile(r'公告')),
                Bs4HtmlField(css_select='.content_right_detail .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='农业银行',
            type_main='公告',
            type_next='采购公告',
            url='http://www.abchina.com/cn/AboutABC/CG/Purchase/default.htm',
            selectors=[
                Bs4AttrTextField(target='href', name='a', attrs={'href': re.compile(r'\.htm|\.html')}, string=re.compile(r'公告')),
                Bs4HtmlField(css_select='.content_right_detail .TRS_Editor', many=False)
            ]
        ),
        # 建设银行 的还有各省份分行 分支 有待爬取
        Target(
            bank_name='建设银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.ccb.com/cn/v3/include/notice/zxgg_1.html',
            selectors=[
                Bs4AttrTextField(target='href', name='a', attrs={'href': re.compile(r'\.htm|\.html'), 'class': 'blue3', 'title': True}),
                Bs4HtmlField(attrs={'id': 'ti'}, many=False)
            ]
        ),
        Target(
            bank_name='交通银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.bankcomm.com/BankCommSite/shtml/jyjr/cn/7158/7162/list_1.shtml',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.main ul.tzzgx-conter.ty-list li a'),
                Bs4HtmlField(attrs={'class': 'show_main c_content'}, many=False)
            ]
        ),
        Target(
            bank_name='邮储银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.psbc.com/cn/index/syycxw/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#article_1 li.clearfix a'),
                Bs4HtmlField(attrs={'class': 'news_cont_msg'}, many=False)
            ]
        ),
        Target(
            bank_name='邮储银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.psbc.com/cn/index/ggl/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#article_1 li.clearfix a'),
                Bs4HtmlField(attrs={'class': 'news_cont_msg'}, many=False)
            ]
        ),


        Target(
            bank_name='中信银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.citicbank.com/about/companynews/banknew/message/%s/index.html' % time.strftime('%Y'),
            selectors=[
                Bs4AttrTextField(target='href', css_select='#business ul.dhy_b li a'),
                Bs4HtmlField(attrs={'class': re.compile(r'TRS_Editor|main_content')}, many=False)
            ]
        ),
        Target(
            bank_name='中信银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.citicbank.com/about/companynews/zxsh/',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#business ul.dhy_b li a'),
                Bs4HtmlField(attrs={'class': re.compile(r'TRS_Editor|main_content')}, many=False)
            ]
        ),
        Target(
            bank_name='中信银行',
            type_main='公告',
            type_next='服务公告',
            url='http://www.citicbank.com/common/servicenotice/',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#business ul.dhy_b li a'),
                Bs4HtmlField(attrs={'class': re.compile(r'TRS_Editor|main_content')}, many=False)
            ]
        ),
        Target(
            bank_name='招商银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.cmbchina.com/cmbinfo/news/',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#column_content span.c_title a'),
                Bs4HtmlField(attrs={'class': re.compile(r'infodiv|c_content')}, many=False)
            ]
        ),
        Target(
            bank_name='招商银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.cmbchina.com/cmbinfo/news/',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#column_content span.c_title a'),
                Bs4HtmlField(css_select='#column_content .c_content', many=False)
            ]
        ),

        Target(
            bank_name='民生银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.cmbc.com.cn/jrms/msdt/msxw/index.htm',
            selectors=[
                Bs4AttrTextField(target='href', css_select='li.left_ul520 a'),
                Bs4HtmlField(css_select='.counter_mid .count_table', many=False)
            ]
        ),
        Target(
            bank_name='民生银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.cmbc.com.cn/jrms/msdt/mtgz/index.htm',
            selectors=[
                Bs4AttrTextField(target='href', css_select='li.left_ul520 a'),
                Bs4HtmlField(css_select='.counter_mid .count_table', many=False)
            ]
        ),
        Target(
            bank_name='民生银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.cmbc.com.cn/zdtj/zygg/index.htm',
            selectors=[
                Bs4AttrTextField(target='href', css_select='li.left_ul520 a'),
                Bs4HtmlField(css_select='.counter_mid_1 .count_one', many=False)
            ]
        ),
        Target(
            bank_name='民生银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.cmbc.com.cn/jrms/msdt/fykyzq/index.htm',
            selectors=[
                Bs4AttrTextField(target='href', css_select='li.left_ul520 a'),
                Bs4HtmlField(css_select='.counter_mid .count_table', many=False)
            ]
        ),

        # 浦发银行的采购公告是PDF文件格式，后期再添加解析PDF文件的功能
        Target(
            bank_name='浦发银行',
            type_main='新闻',
            type_next='来源本行',
            url='https://news.spdb.com.cn/about_spd/xwdt_1632/index.shtml',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.c_news_body ul li a'),
                Bs4HtmlField(css_select='.fixed_width .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='浦发银行',
            type_main='新闻',
            type_next='来源本行',
            url='https://news.spdb.com.cn/about_spd/media/index.shtml',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.c_news_body ul li a'),
                Bs4HtmlField(css_select='.fixed_width .TRS_Editor', many=False)
            ]
        ),

        Target(
            bank_name='兴业银行',
            type_main='新闻',
            type_next='来源本行',
            url='https://www.cib.com.cn/cn/aboutCIB/about/news/',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.list-box .middle ul:nth-of-type(2) li a'),
                Bs4HtmlField(css_select='.detail-box .middle', many=False)
            ]
        ),
        Target(
            bank_name='兴业银行',
            type_main='公告',
            type_next='其他公告',
            url='https://www.cib.com.cn/cn/aboutCIB/about/notice/',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.list-box .middle ul:nth-of-type(2) li a'),
                Bs4HtmlField(css_select='.detail-box .middle', many=False)
            ]
        ),

        Target(
            bank_name='平安银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://bank.pingan.com/ir/gonggao/xinwen/index.shtml',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.span10 ul.list li a'),
                Bs4HtmlField(css_select='.container .row:last-of-type .span10 .row .span10 .box', many=False)
            ]
        ),
        Target(
            bank_name='广发银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.cgbchina.com.cn/Channel/11625977',
            selectors=[
                Bs4AttrTextField(target='href', css_select='ul.newList li a'),
                Bs4HtmlField(css_select='#textContent .textContent', many=False)
            ]
        ),
        Target(
            bank_name='广发银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.cgbchina.com.cn/Channel/11640277',
            selectors=[
                Bs4AttrTextField(target='href', css_select='ul.newList li a'),
                Bs4HtmlField(attrs={'id': 'textContent'}, many=False)
            ]
        ),

        Target(
            bank_name='光大银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.cebbank.com/site/ceb/gddt/xnxw52/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#main_con ul.gg_right_ul li a'),
                Bs4HtmlField(css_select='.gd_xilan .xilan_con', many=False)
            ]
        ),
        Target(
            bank_name='光大银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.cebbank.com/site/ceb/gddt/mtgz/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#main_con ul.gg_right_ul li a'),
                Bs4HtmlField(css_select='.gd_xilan .xilan_con', many=False)
            ]
        ),
        Target(
            bank_name='光大银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.cebbank.com/site/zhpd/zxgg35/gdgg10/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#gg_right ul.gg_right_ul li a'),
                Bs4HtmlField(css_select='.gd_xilan .xilan_con', many=False)
            ]
        ),
        Target(
            bank_name='光大银行',
            type_main='公告',
            type_next='采购公告',
            url='http://www.cebbank.com/site/zhpd/zxgg35/cggg/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#gg_right ul.gg_right_ul li a'),
                Bs4HtmlField(css_select='.gd_xilan .xilan_con', many=False)
            ]
        ),
        Target(
            bank_name='光大银行',
            type_main='公告',
            type_next='采购公告',
            url='http://www.cebbank.com/site/zhpd/zxgg35/cgjggg/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#gg_right ul.gg_right_ul li a'),
                Bs4HtmlField(css_select='.gd_xilan .xilan_con', many=False)
            ]
        ),

        Target(
            bank_name='华夏银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.hxb.com.cn/jrhx/hxzx/hxxw/index.shtml',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.pro_contlist ul li.pro_contli a'),
                Bs4HtmlField(attrs={'id': 'content'}, many=False)
            ]
        ),
        Target(
            bank_name='华夏银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.hxb.com.cn/jrhx/khfw/zxgg/index.shtml',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.pro_contlist ul li.pro_contli a'),
                Bs4HtmlField(attrs={'id': 'content'}, many=False)
            ]
        ),
        Target(
            bank_name='浙商银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.czbank.com/cn/pub_info/news/',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#content dd a'),
                Bs4HtmlField(css_select='.cdv_content .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='浙商银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.czbank.com/cn/pub_info/important_notice/',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.list_content dd a'),
                Bs4HtmlField(css_select='.cdv_content .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='浙商银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.czbank.com/cn/pub_info/Outside_reports/',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.list_content dd a'),
                Bs4HtmlField(css_select='.cdv_content .TRS_Editor', many=False)
            ]
        ),

        Target(
            bank_name='恒丰银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.hfbank.com.cn/gyhf/hfxw/index.shtml',
            selectors=[
                Bs4AttrTextField(target='href', css_select='#imgArticleList li h3 a'),
                Bs4HtmlField(css_select='.infoArticle .articleCon', many=False)
            ]
        ),
        Target(
            bank_name='恒丰银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.hfbank.com.cn/gryw/yhgg/index.shtml',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.annWrap li h3 a'),
                Bs4HtmlField(css_select='.infoArticle .articleCon', many=False)
            ]
        ),

        Target(
            bank_name='北京银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.bankofbeijing.com.cn/about/gonggao.html',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#area .content_left ul.sub_news li span a',
                    url_prefix='http://www.bankofbeijing.com.cn/'),
                Bs4HtmlField(attrs={'id': 'con'}, many=False)
            ]
        ),
        Target(
            bank_name='贵阳银行',
            type_main='公告',
            type_next='其他公告',
            url='https://www.bankgy.cn/portal/zh_CN/home/news/notice/list.html',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='.detailConter .mewlist ul li a[href^="news/notice/2020"]',
                    url_prefix='https://www.bankgy.cn/portal/zh_CN/home/'),
                Bs4HtmlField(css_select='.detailConter .textConter', many=False)
            ]
        ),
        Target(
            bank_name='贵阳银行',
            type_main='新闻',
            type_next='来源本行',
            url='https://www.bankgy.cn/portal/zh_CN/home/news/dynamic/list.html',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='.detailConter .mewlist ul li a[href^="news/dynamic/2020"]',
                    url_prefix='https://www.bankgy.cn/portal/zh_CN/home/'),
                Bs4HtmlField(css_select='.detailConter .textConter', many=False)
            ]
        ),
        Target(
            bank_name='杭州银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.hzbank.com.cn/hzyh/index/bxgg/index.html',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#yc_main .portlet ul.new_list1 li span:first-of-type a[href^="/hzyh/index/bxgg/"]',
                    url_prefix='http://www.hzbank.com.cn/'),
                Bs4HtmlField(css_select='#easysiteText', many=False)
            ]
        ),
        Target(
            bank_name='杭州银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.hzbank.com.cn/hzyh/index/bxkx/index.html',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#yc_main .portlet ul.new_list1 li span:first-of-type a[href^="/hzyh/index/bxkx/"]',
                    url_prefix='http://www.hzbank.com.cn/'),
                Bs4HtmlField(css_select='#easysiteText', many=False)
            ]
        ),

        Target(
            bank_name='江苏银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.jsbchina.cn/CN/zygg/index.html?flag=0',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#myTab0_Content ul a[href^="/CN/zygg/"]',
                    url_prefix='http://www.jsbchina.cn/'),
                Bs4HtmlField(css_select='#myTab0_Content0', many=False)
            ]
        ),
        Target(
            bank_name='江苏银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.jsbchina.cn/CN/gywh/ggywh/gwhxx/index.html?flag=3',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#myTab0_Content ul a[href^="/CN/gywh/ggywh/gwhxx/"]',
                    url_prefix='http://www.jsbchina.cn/'),
                Bs4HtmlField(css_select='#myTab0_Content0', many=False)
            ]
        ),
        Target(
            bank_name='江苏银行',
            type_main='新闻',
            type_next='来源媒体',
            url='http://www.jsbchina.cn/CN/gywh/ggywh/gmtgz/index.html?flag=1',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#myTab0_Content ul a[href^="/CN/gywh/ggywh/gmtgz/"]',
                    url_prefix='http://www.jsbchina.cn/'),
                Bs4HtmlField(css_select='#myTab0_Content0', many=False)
            ]
        ),

        Target(
            bank_name='南京银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.njcb.com.cn/njcb/index/_301021/index.html',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#right_lib .erjilib_mk .erjilib_mkcon .erji_libcon .erji_lib p.erji_libtit a',
                    url_prefix='http://www.njcb.com.cn'),
                Bs4HtmlField(css_select='#news_content', many=False)
            ]
        ),
        Target(
            bank_name='南京银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.njcb.com.cn/njcb/gywx/xwzx/index.html',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#right_lib .erjilib_mk .erjilib_mkcon .erji_libcon .erji_lib p.erji_libtit a',
                    url_prefix='http://www.njcb.com.cn'),
                Bs4HtmlField(css_select='#news_content', many=False)
            ]
        ),
        Target(
            bank_name='南京银行',
            type_main='新闻',
            type_next='来源媒体',
            url='http://www.njcb.com.cn/njcb/gywx/_300910/index.html',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#right_lib .erjilib_mk .erjilib_mkcon .erji_libcon .erji_lib p.erji_libtit a',
                    url_prefix='http://www.njcb.com.cn'),
                Bs4HtmlField(css_select='#news_content', many=False)
            ]
        ),

        Target(
            bank_name='宁波银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.nbcb.com.cn/home/important_notices/',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#ul_list li a',
                    url_prefix='http://www.nbcb.com.cn/home/important_notices/'),
                Bs4HtmlField(css_select='#cms_wrapper .cms_cont', many=False)
            ]
        ),
        Target(
            bank_name='宁波银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.nbcb.com.cn/investor_relations/internal_news/',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#ul_list li a',
                    url_prefix='http://www.nbcb.com.cn/investor_relations/internal_news/'),
                Bs4HtmlField(css_select='#cms_wrapper .cms_cont', many=False)
            ]
        ),
        Target(
            bank_name='宁波银行',
            type_main='新闻',
            type_next='来源媒体',
            url='http://www.nbcb.com.cn/investor_relations/media_release/',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='#ul_list li a',
                    url_prefix='http://www.nbcb.com.cn/investor_relations/media_release/'),
                Bs4HtmlField(css_select='#cms_wrapper .cms_cont', many=False)
            ]
        ),

        Target(
            bank_name='青岛银行',
            type_main='新闻',
            type_next='来源媒体',
            url='http://www.qdccb.com/qyxx/xnxx/mtkwx/index.shtml',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='.tableList tr td:nth-of-type(2) a[href^="/qyxx/xnxx/mtkwx/"]',
                    url_prefix='http://www.qdccb.com/'),
                Bs4HtmlField(css_select='.main .second_right .second_rightContent', many=False)
            ]
        ),

        Target(
            bank_name='上海银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.bosc.cn/zh/sy/sy_zxgg/index.shtml',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='ul.dzyhdt a[href^="/zh/sy/sy_zxgg/"]',
                    url_prefix='http://www.bosc.cn/'),
                Bs4HtmlField(css_select='div.fr.w706 > div.m_smaBor.mt15 > div > div', many=False)
            ]
        ),
        Target(
            bank_name='上海银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.bosc.cn/zh/sy/sy_sykx/index.shtml',
            selectors=[
                Bs4AttrTextField(
                    target='href',
                    css_select='ul.dzyhdt a[href^="/zh/sy/sy_sykx/"]',
                    url_prefix='http://www.bosc.cn/'),
                Bs4HtmlField(css_select='div.fr.w706 > div.m_smaBor.mt15 > div > div', many=False)
            ]
        ),

        Target(
            bank_name='苏州银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.suzhoubank.com/icms/static/szbank/zh/0d6u9hrt/yvngsgtq/7d99gtx7/x1nwoo1t/pageInfo.txt',
            selectors=[
                JsonMultiField(json_select='url=title=date', url_prefix='http://www.suzhoubank.com/icms/'),
                Bs4HtmlField(css_select='div.index-main > div.wp > div.fr.right > div.huodong > div.dzyh_main', many=False)
            ]
        ),
        Target(
            bank_name='苏州银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.suzhoubank.com/icms/static/szbank/zh/0d6u9hrt/yvngsgtq/7d99gtx7/46idcb1g/pageInfo.txt',
            selectors=[
                JsonMultiField(json_select='url=title=date', url_prefix='http://www.suzhoubank.com/icms/'),
                Bs4HtmlField(css_select='div.index-main > div.wp > div.fr.right > div.huodong > div.dzyh_main', many=False)
            ]
        ),

        Target(
            bank_name='西安银行',
            type_main='新闻',
            type_next='来源本行',
            url='https://www.xacbank.com/icms/static/xacbank2019/zh/jvsxapz8/jo1txlfm/y2zpei09/pageInfo.txt?t=%s' % int(time.time() * 1000),
            selectors=[
                JsonMultiField(json_select='url=title=date', url_prefix='https://www.xacbank.com/icms/'),
                Bs4HtmlField(css_select='#text_css', many=False)
            ]
        ),

        Target(
            bank_name='长沙银行',
            type_main='公告',
            type_next='采购公告',
            url='http://www.cscb.cn/home_noticeInfo_bidding_page1.html',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='.box_cont .body_area .jd_list ul li a',
                                 url_prefix='http://www.cscb.cn/'),
                Bs4HtmlField(css_select='.body_area .img_wd_lie .sxd_sq', many=False)
            ]
        ),
        Target(
            bank_name='长沙银行',
            type_main='公告',
            type_next='服务公告',
            url='http://www.cscb.cn/home_noticeInfo_announcement_page1.html',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='.box_cont .body_area .jd_list ul li a',
                                 url_prefix='http://www.cscb.cn/'),
                Bs4HtmlField(css_select='.body_area .img_wd_lie .sxd_sq', many=False)
            ]
        ),
        Target(
            bank_name='长沙银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.cscb.cn/home_news_page1.html',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='.box_cont .body_area .jd_list ul li a',
                                 url_prefix='http://www.cscb.cn/'),
                Bs4HtmlField(css_select='.body_area .img_wd_lie .sxd_sq', many=False)
            ]
        ),
        Target(
            bank_name='郑州银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.zzbank.cn/about/zxdt/zxgg/',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='.main_right .message_list .paginationBar ul li a',
                                 url_prefix='http://www.zzbank.cn/about/zxdt/zxgg/'),
                Bs4HtmlField(css_select='.main_right .message_list .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='郑州银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.zzbank.cn/about/zxdt/gsdt/',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='.main_right .message_list .paginationBar ul li a',
                                 url_prefix='http://www.zzbank.cn/about/zxdt/gsdt/'),
                Bs4HtmlField(css_select='.main_right .message_list .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='郑州银行',
            type_main='新闻',
            type_next='来源媒体',
            url='http://www.zzbank.cn/about/zxdt/mtbg/',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='.main_right .message_list .paginationBar ul li a',
                                 url_prefix='http://www.zzbank.cn/about/zxdt/mtbg/'),
                Bs4HtmlField(css_select='.main_right .message_list .TRS_Editor', many=False)
            ]
        ),

        Target(
            bank_name='常熟银行',
            type_main='公告',
            type_next='采购公告',
            url='http://www.csrcbank.com/yw/cgxx/cggg/',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='ul#data li a',
                                 url_prefix='http://www.csrcbank.com/yw/cgxx/cggg/'),
                Bs4HtmlField(css_select='#tabstyle .TRS_Editor', many=False)
            ]
        ),
        Target(
            bank_name='常熟银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.csrcbank.com/tb/tzgg/',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='ul#data li a',
                                 url_prefix='http://www.csrcbank.com/tb/tzgg/'),
                Bs4HtmlField(css_select='#tabstyle .TRS_Editor', many=False)
            ]
        ),

        Target(
            bank_name='江阴银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.jybank.com.cn/jybank/index/zygg/index.html',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='#text .recruitment-con ul li a',
                                 url_prefix='http://www.jybank.com.cn/'),
                Bs4HtmlField(css_select='.news .news_con', many=False)
            ]
        ),
        Target(
            bank_name='江阴银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.jybank.com.cn/jybank/index/xyxw/index.html',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='#text .recruitment-con ul li a',
                                 url_prefix='http://www.jybank.com.cn/'),
                Bs4HtmlField(css_select='.news .news_con', many=False)
            ]
        ),

        Target(
            bank_name='青农银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.qrcb.com.cn/qrcbcms/html/zdgg/',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='.main_right .box4 ul li .tit2 a:last-of-type',
                                 url_prefix='http://www.qrcb.com.cn/'),
                Bs4HtmlField(css_select='.main_right .box5 .zhengwen_con1', many=False)
            ]
        ),

        Target(
            bank_name='苏农银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.szrcb.com/wjrcb/gdgg/xwgg/index.html?v=%s' % int(time.time() * 1000),
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='ul li a[href^="/wjrcb/gdgg/xwgg/"]',
                                 url_prefix='http://www.szrcb.com/'),
                Bs4HtmlField(css_select='.bg-ff .main-lc .lccpbox .lbright .ggpad', many=False)
            ]
        ),
        Target(
            bank_name='苏农银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.szrcb.com/wjrcb/gdgg/wjxw/index.html?v=%s' % int(time.time() * 1000),
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='ul li a[href^="/wjrcb/gdgg/wjxw/"]',
                                 url_prefix='http://www.szrcb.com/'),
                Bs4HtmlField(css_select='.bg-ff .main-lc .lccpbox .lbright .ggpad', many=False)
            ]
        ),

        Target(
            bank_name='无锡银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.wrcb.com.cn/website/homepage/bank_notice_news_list/index.html',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='#frmList .yhkyw_box .content_p table tr td:first-of-type a',
                                 url_prefix='http://www.wrcb.com.cn/'),
                Bs4HtmlField(css_select='.main_r .yhkyw_box', many=False)
            ]
        ),
        Target(
            bank_name='无锡银行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.wrcb.com.cn/website/homepage/bank_news_list/index.html',
            selectors=[
                Bs4AttrTextField(target='href',
                                 css_select='#frmList .yhkyw_box .content_p table tr td:first-of-type a',
                                 url_prefix='http://www.wrcb.com.cn/'),
                Bs4HtmlField(css_select='.main_r .yhkyw_box', many=False)
            ]
        ),

        Target(
            bank_name='张家港行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.zrcbank.com/',
            selectors=[
                Bs4AttrField(target='onclick',
                             name='div',
                             attrs={'onclick': re.compile(r'window\.location\.href=')},
                             string='重要公告',
                             callback='parse_zrcbank',
                             many=False),
                Bs4AttrTextField(target='href', css_select='#divdemo ul li a', url_prefix='http://www.zrcbank.com/'),
                Bs4HtmlField(css_select='#divdemo', many=False)
            ]
        ),
        Target(
            bank_name='张家港行',
            type_main='新闻',
            type_next='来源本行',
            url='http://www.zrcbank.com/',
            selectors=[
                Bs4AttrField(target='onclick',
                             name='div',
                             attrs={'onclick': re.compile(r'window\.location\.href=')},
                             string='银行新闻',
                             callback='parse_zrcbank',
                             many=False),
                Bs4AttrTextField(target='href', css_select='#divdemo ul li a', url_prefix='http://www.zrcbank.com/'),
                Bs4HtmlField(css_select='#divdemo', many=False)
            ]
        ),

        Target(
            bank_name='紫金银行',
            type_main='公告',
            type_next='其他公告',
            url='http://www.zjrcbank.com/zygg/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.RightSidebar .mianContent ul li a', url_prefix='http://www.zjrcbank.com/'),
                Bs4HtmlField(css_select='.RightSidebar .mianContent .News_Info .txt_info', many=False)
            ]
        ),
        Target(
            bank_name='紫金银行',
            type_main='公告',
            type_next='采购公告',
            url='http://www.zjrcbank.com/ytcggg/index.html',
            selectors=[
                Bs4AttrTextField(target='href', css_select='.RightSidebar .mianContent ul li a', url_prefix='http://www.zjrcbank.com/'),
                Bs4HtmlField(css_select='.RightSidebar .mianContent .News_Info .txt_info', many=False)
            ]
        ),
    }
