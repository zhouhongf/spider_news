# ukey          银行名称=code
# bank_name     银行名称
# file_type     产品说明书、产品发行公告、产品成立公告、产品终止公告
# file_suffix   文件类型.pdf, .docx等
# content       bytes内容
# name          理财产品名称， 如果没有名称，则默认使用ukey做名称
# create_time   创建时间
# status        状态

import time
import farmhash


class Document(object):
    """
    用于保存 产品说明书PDF文件，成立公告PDF，到期公告PDF等文件的类
    ukey=bank_name=时间
    """

    def __init__(
            self,
            ukey: str,
            file_type: str,
            file_suffix: str,
            content: str,
            status: str = 'undo',
            create_time: str = time.strftime('%Y-%m-%d %H:%M:%S')
    ):
        self._ukey = ukey
        words = ukey.split('=')
        self._bank_name = words[0]
        self._file_type = file_type
        self._file_suffix = file_suffix
        self._content = content
        self._create_time = create_time
        self._status = status

    def __repr__(self):
        return f"【ukey: {self._ukey}, file_type: {self._file_type}, file_suffix: {self._file_suffix}, 'create_time': {self._create_time},  'status': {self._status}】"

    def do_dump(self):
        elements = [one for one in dir(self) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        data = {}
        for name in elements:
            data[name] = getattr(self, name, None)
        data['_id'] = str(farmhash.hash64(self.ukey))
        return data

    @property
    def ukey(self):
        return self._ukey

    @ukey.setter
    def ukey(self, value):
        self._ukey = value

    @property
    def bank_name(self):
        return self._bank_name

    @bank_name.setter
    def bank_name(self, value):
        self._bank_name = value

    @property
    def file_type(self):
        return self._file_type

    @file_type.setter
    def file_type(self, value):
        self._file_type = value

    @property
    def file_suffix(self):
        return self._file_suffix

    @file_suffix.setter
    def file_suffix(self, value):
        self._file_suffix = value

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, value):
        self._create_time = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
