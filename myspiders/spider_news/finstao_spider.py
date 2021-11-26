from myspiders.base import Spider, Response, MainContent, JsonMultiField
from config import Rules, Target, Paper, Tweet, TweetPhoto, TweetComment, UserProfile, UserAvatar
import aiohttp
import async_timeout
import time
import random
import math

'''
{
'code': 0, 
'data': 
    {
        'access_token': '4a49e960-9bc2-11ea-8666-a9e6ccd396b9', 
        'user': {
            'id': 104549, 
            'password': True, 
            'mobile': '15716252839', 
            'email': '', 
            'create_time': 1590106048000,
            'update_time': 1590106083000, 
            'avatar_id': 0, 
            'nickname': '惠生', 
            'gender': 2, 
            'intro': '', 
            'birthday': '', 
            'company': '', 
            'job': '', 
            'domain': '', 
            'level': 1, 
            'vip': 0, 
            'admin': 0, 
            'like_count': 0, 
            'write_count': 0, 
            'followee_count': 0, 
            'follower_count': 0, 
            'avatar': '//img.finstao.com/avatar_female.jpg'
            }
    }, 
'msg': 'success', 
'ts': 1590106936053
}
'''


def formdata_tweet(access_token: str, page_index: int):
    formdata = {
        "page_size": 10,
        "sort_by": "create_time",
        "sort_order": "desc",
        "page": page_index,
        "seed": int(time.time() * 1000),
        "counter": 1,
        "query": "",
        "access_token": access_token,
        "os_name": "android",
        "os_version": 23,
        "app_version": "2.5.4"
    }
    return formdata


def formdata_comments(access_token: str, page_index: int, tweet_id: str):
    formdata = {
        "page": page_index,
        "seed": int(time.time() * 1000),
        "counter": 1,
        "query": "",
        "page_size": 10,
        "sort_by": "create_time",
        "sort_order": "desc",
        "tweet_id": int(tweet_id),
        "all": 1,
        "access_token": access_token,
        "os_name": "android",
        "os_version": 23,
        "app_version": "2.5.4"
    }
    return formdata


class FinstaoSpider(Spider):
    name = 'FinstaoSpider'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; OPPO R9s Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36 finstao_app/2.5.4'}
    login_url = 'https://api.finstao.com/v1/auth/signin'
    login_data = [
        {
            "username": "13771880835",
            "password": "19851230",
            "os_name": "android",
            "os_version": 23,
            "app_version": "2.5.4"
        },
        {
            "username": "15716252839",
            "password": "20110919",
            "os_name": "android",
            "os_version": 23,
            "app_version": "2.5.4"
        },
    ]
    currentUser = {}
    currentCookie = ''
    page_size = 10
    tweet_url = 'https://api.finstao.com/v1/search/tweet'
    tweet_comment_url = 'https://api.finstao.com/v1/tweet/comment/list'

    virtual_user_prefix = 'VRUSER'
    tweet_prefix = 'MYWEET'
    tweet_photo_prefix = 'TPHOTO'
    tweet_comment_prefix = 'TCOMNT'
    extension_jpg = '.jpg'

    async def manual_start_urls(self):
        formdata = random.choice(self.login_data)
        async with aiohttp.ClientSession() as client:
            async with client.post(url=self.login_url, headers=self.headers, data=formdata, timeout=15) as response:
                assert response.status == 200
                headers = response.headers
                cookie_need = headers.get('Set-Cookie')
                cookie = cookie_need.split(';')[0]
                print('============ cookie是：', cookie)
                self.headers.update({'cookie': cookie})
                print('============ headers是：', self.headers)
                jsondata = await response.json()
                self.currentUser = jsondata['data']
                access_token = self.currentUser['access_token']
                # 每次抓取前10页内容
                for index in range(1, 11):
                    with async_timeout.timeout(15):
                        formdata = formdata_tweet(access_token, index)
                        yield self.request(url=self.tweet_url, headers=self.headers, form_data=formdata, callback=self.parse)

    async def parse(self, response):
        jsondata = await response.json()
        list_data = jsondata['data']['list']
        for data in list_data:
            one = data['tweet']
            user = one['user']
            images = one['images']
            if not user['id']:
                print('============= ', user)
            # 保存用户资料和用户头像
            yield self.save_user_profile(user)
            # 保存微博信息
            yield self.save_tweet(tweet=one, user=user)

            user_id = str(user['id']) if user['id'] else '0'
            tweet_id = str(one['id'])
            # 如果该微博有图片的，则下载图片
            if images:
                for image in images:
                    url = image['url']
                    if url:
                        url = url if url.startswith('http') else 'http:' + url
                        yield self.request(url=url, headers=self.headers, callback=self.save_tweet_photo, metadata={'data': image, 'tweet_id': tweet_id, 'user_id': user_id})

            # 如果该微博有评论的，则下载评论内容，包括发布该评论的用户信息，也一起下载
            sub_count = one['sub_count']
            if sub_count > 0:
                page_num = math.ceil(sub_count / self.page_size)
                for index in range(1, page_num + 1):
                    formdata = formdata_comments(access_token=self.currentUser['access_token'], page_index=index, tweet_id=tweet_id)
                    yield self.request(url=self.tweet_comment_url, headers=self.headers, form_data=formdata, callback=self.parse_comment, metadata={'tweet_id': tweet_id})

    async def save_tweet_photo(self, response):
        photo = response.metadata['data']
        tweet_id = response.metadata['tweet_id']
        user_id = response.metadata['user_id']

        content = await response.read()
        tweet_photo = TweetPhoto(
            _id=self.tweet_photo_prefix + str(photo['id']),
            user_wid=self.virtual_user_prefix + user_id,
            tweet_wid=self.tweet_prefix + tweet_id,

            file_name=self.tweet_photo_prefix + str(photo['id']) + self.extension_jpg,
            extension_type='image/jpeg',
            file_byte=content,
            size=photo['size']
        )
        data = tweet_photo.do_dump()
        print('==============save_tweet_photo方法，保存：', data['_id'])
        self.collection_tweet_photo.update_one({'_id': data['_id']}, {'$set': data}, upsert=True)
        # 更新tweet中的tweet_photos
        tweet = self.collection_tweet.find_one({'_id': data['tweet_wid']})
        tweet_photos = tweet['tweet_photos']
        if not tweet_photos:
            tweet['tweet_photos'] = data['_id'] + ','
        else:
            tweet['tweet_photos'] = tweet_photos + data['_id'] + ','
        self.collection_tweet.update_one({'_id': tweet['_id']}, {'$set': tweet})


    async def parse_comment(self, response):
        jsondata = await response.json()
        tweet_id = response.metadata['tweet_id']
        comments = jsondata['data']['list']
        for one in comments:
            commenter = one['user']
            # 保存评论者的用户信息
            yield self.save_user_profile(commenter)
            # 保存评论内容
            yield self.save_tweet_comment(comment=one, tweet_id=tweet_id, commenter=commenter)

    async def save_tweet_comment(self, comment, tweet_id, commenter):
        keys_user = commenter.keys()
        commenter_id = commenter['id']
        tweet_comment = TweetComment(
            _id=self.tweet_comment_prefix + str(comment['id']),
            tweet_wid=self.tweet_prefix + str(tweet_id),
            comment=comment['content'],
            commenter_wid=self.virtual_user_prefix + str(commenter_id),
            nickname=commenter['nickname'] if 'nickname' in keys_user else '',
            position=commenter['job'] if 'job' in keys_user else '',
            company=commenter['company'] if 'company' in keys_user else '',

            commentat_wid='',
            like_count=comment['like_count'],
            create_time=comment['create_time']
        )
        data = tweet_comment.do_dump()
        data_filter = self.filter_keyword(data)
        if data_filter:
            print('==============save_tweet_comment方法，保存：', data['_id'])
            self.collection_tweet_comment.update_one({'_id': data['_id']}, {'$set': data}, upsert=True)
            # 更新tweet中的tweet_comments
            tweet = self.collection_tweet.find_one({'_id': data['tweet_wid']})
            tweet_comments = tweet['tweet_comments']
            if not tweet_comments:
                tweet['tweet_comments'] = data['_id'] + ','
            else:
                tweet['tweet_comments'] = tweet_comments + data['_id'] + ','
            self.collection_tweet.update_one({'_id': tweet['_id']}, {'$set': tweet})

    async def save_tweet(self, tweet, user):
        user_id = str(user['id']) if user['id'] else '0'
        keys = tweet.keys()
        keys_user = user.keys()
        tweet_need = Tweet(
            _id=self.tweet_prefix + str(tweet['id']),
            anonymous=tweet['anonymous'] if 'anonymous' in keys else 0,
            user_wid=self.virtual_user_prefix + str(user_id),
            nickname=user['nickname'] if 'nickname' in keys_user else '',
            position=user['job'] if 'job' in keys_user else '',
            company=user['company'] if 'company' in keys_user else '',

            content=tweet['content'] if 'content' in keys else '',
            tweet_photos='',
            tweet_comments='',

            can_share=tweet['can_share'] if 'can_share' in keys else False,
            share_count=tweet['forward_count'] if 'forward_count' in keys else 0,

            favor_count=tweet['favor_count'] if 'favor_count' in keys else 0,
            view_count=tweet['view_count'] if 'view_count' in keys else 0,
            like_count=tweet['like_count'] if 'like_count' in keys else 0,
            comment_count=tweet['sub_count'] if 'sub_count' in keys else 0,

            create_time=tweet['create_time'] if 'create_time' in keys else 0,
            update_time=tweet['update_time'] if 'update_time' in keys else 0,
        )
        data = tweet_need.do_dump()
        print('==============save_tweet方法，保存：', data['_id'])
        data_filter = self.filter_keyword(data)
        if data_filter:
            self.collection_tweet.update_one({'_id': data['_id']}, {'$set': data}, upsert=True)

    def filter_keyword(self, data):
        nickname = data['nickname'].lower()
        company = data['company'].lower()
        position = data['position'].lower()
        filter_one = '今融'
        filter_two = 'finstao'
        if filter_one in nickname or filter_one in company or filter_one in position:
            return False
        if filter_two in nickname or filter_two in company or filter_two in position:
            return False
        return True


    async def save_user_profile(self, user):
        keys = user.keys()
        user_id = str(user['id']) if user['id'] else '0'
        user_profile = UserProfile(
            _id=self.virtual_user_prefix + user_id,
            intro=user['intro'] if 'intro' in keys else '',
            nickname=user['nickname'] if 'nickname' in keys else '',
            email=user['email'] if 'email' in keys else '',
            idtype='',
            position=user['job'] if 'job' in keys else '',
            industry='',
            company=user['company'] if 'company' in keys else '',
            placebelong='',
            address='',
            gender=user['gender'] if 'gender' in keys else 0,
            create_time=user['create_time'] if 'create_time' in keys else 0,
            update_time=user['update_time'] if 'update_time' in keys else 0,
        )
        data = user_profile.do_dump()
        print('==============save_user_profile方法，保存：', data['_id'])
        self.collection_tweet_userprofile.update_one({'_id': data['_id']}, {'$set': data}, upsert=True)
        # 保存好用户资料后，继续下载用户头像图片，然后保存
        avatar = user['avatar'] if 'avatar' in keys else ''
        if avatar:
            avatar = avatar if avatar.startswith('http') else 'http:' + avatar
            yield self.request(url=avatar, headers=self.headers, callback=self.save_user_avatar, metadata={'data': data})

    async def save_user_avatar(self, response):
        user = response.metadata['data']
        content = await response.read()
        if content:
            user_avatar = UserAvatar(
                _id=user['_id'],
                file_name=user['_id'] + self.extension_jpg,
                extension_type='image/jpeg',
                file_byte=content
            )
            data = user_avatar.do_dump()
            print('==============save_user_avatar方法，保存：', data['_id'])
            self.collection_tweet_useravatar.update_one({'_id': data['_id']}, {'$set': data}, upsert=True)


def start():
    FinstaoSpider.start()
    # pass
