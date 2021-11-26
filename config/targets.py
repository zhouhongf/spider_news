
class Targets:

    def __init__(
            self,
            bank_name: str,
            type_main: str,
            type_next: str,
            urls: list,
            type_one: str = None,
            type_two: str = None,
            type_three: str = None,
            method: str = 'GET',
            headers: dict = None,
            formdata: dict = None,
            callback: str = None,
            metadata: dict = None,
            selectors: list = None,
    ):
        self._bank_name = bank_name
        self._type_main = type_main
        self._type_next = type_next
        self._urls = urls or []
        self._type_one = type_one
        self._type_two = type_two
        self._type_three = type_three
        self._method = method
        self._headers = headers or {}
        self._formdata = formdata or {}
        self._callback = callback
        self._metadata = metadata or {}
        self._selectors = selectors

    def __repr__(self):
        return f"【bank_name: {self._bank_name}, type_main: {self._type_main}, urls: {self._urls}, method: {self._method}, formdata: {self._formdata}, callback: {self._callback}, selectors: {self._selectors}】"

    def do_dump(self):
        elements = [one for one in dir(self) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        data = {}
        for name in elements:
            data[name] = getattr(self, name, None)
        return data

    @property
    def urls(self):
        return self._urls

    @urls.setter
    def urls(self, value):
        self._urls = value

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        self._method = value

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = value

    @property
    def formdata(self):
        return self._formdata

    @formdata.setter
    def formdata(self, value):
        self._formdata = value

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, value):
        self._callback = value

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value


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
    def selectors(self):
        return self._selectors

    @selectors.setter
    def selectors(self, value):
        self._selectors = value
