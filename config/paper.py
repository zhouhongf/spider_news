import time
from .bank_dict import BankDict
import pickle
import farmhash
from bson.binary import Binary


version = "0.1"
version_info = (0, 1, 0, 0)


class Paper:
    """
    用于保存 新闻，公告，业务等文章
    """
    def __init__(
            self,
            bank_name: str,
            name: str,
            url: str,
            type_main: str,
            type_next: str,
            type_one: str = None,
            type_two: str = None,
            type_three: str = None,
            content: str = None,
            photos: str = None,
            status: str = 'undo',
            date: str = time.strftime('%Y-%m-%d %H:%M:%S')
    ):
        self._bank_name = bank_name
        self._type_main = type_main
        self._type_next = type_next
        self._type_one = type_one
        self._type_two = type_two
        self._type_three = type_three
        self._name = name
        self._content = content
        self._date = date
        self._url = url
        self._photos = photos
        self._status = status

    def __repr__(self):
        return f"【bank_name: {self._bank_name}, type_main: {self._type_main}, type_next: {self._type_next}, type_one: {self._type_one}, name: {self._name}, date: {self._date}, url: {self._url}】"

    def do_dump(self):
        elements = [one for one in dir(self) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        # elements.remove('content')
        data = {}
        for name in elements:
            data[name] = getattr(self, name, None)
        data['_id'] = str(farmhash.hash64(self._url))
        data['bank_level'] = BankDict.list_bank_level[self._bank_name]
        # data['content'] = Binary(pickle.dumps(self._content))   # 读取的时候使用pickle.loads()恢复成str格式
        data['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        return data

    @property
    def bank_name(self):
        return self._bank_name

    @bank_name.setter
    def bank_name(self, value):
        self._bank_name = value

    @property
    def type_main(self):
        return self._type_main

    @type_main.setter
    def type_main(self, value):
        self._type_main = value

    @property
    def type_next(self):
        return self._type_next

    @type_next.setter
    def type_next(self, value):
        self._type_next = value

    @property
    def type_one(self):
        return self._type_one

    @type_one.setter
    def type_one(self, value):
        self._type_one = value

    @property
    def type_two(self):
        return self._type_two

    @type_two.setter
    def type_two(self, value):
        self._type_two = value

    @property
    def type_three(self):
        return self._type_three

    @type_three.setter
    def type_three(self, value):
        self._type_three = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def photos(self):
        return self._photos

    @photos.setter
    def photos(self, value):
        self._photos = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
