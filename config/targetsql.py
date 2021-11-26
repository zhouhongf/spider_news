
class TargetSQL:

    def __init__(
            self,
            project_name: str,
            tables_in: list,
            table_out: str,
            sql: str,
            del_table: bool = True,
            out_many: bool = True,
            method: str = 'CREATE',
            type_one: str = None,
            type_two: str = None,
            type_three: str = None,
            callback: str = None,
            metadata: dict = None
    ):
        self._project_name = project_name
        self._tables_in = tables_in
        self._table_out = table_out
        self._sql = sql
        self._del_table = del_table
        self._out_many = out_many
        self._method = method
        self._type_one = type_one
        self._type_two = type_two
        self._type_three = type_three
        self._callback = callback
        self._metadata = metadata or {}

    def __repr__(self):
        return f"【project_name: {self._project_name}, tables_in: {self._tables_in}, table_out: {self._table_out}," \
               f" sql: {self._sql}, del_table: {self._del_table}, out_many: {self._out_many}, method: {self._method}, " \
               f"type_one: {self._type_one}, type_two: {self._type_two}, type_three: {self._type_three}," \
               f"callback: {self._callback}, metadata: {self._metadata}】"

    def do_dump(self):
        elements = [one for one in dir(self) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        data = {}
        for name in elements:
            data[name] = getattr(self, name, None)
        return data

    @property
    def project_name(self):
        return self._project_name

    @project_name.setter
    def project_name(self, value):
        self._project_name = value

    @property
    def tables_in(self):
        return self._tables_in

    @tables_in.setter
    def tables_in(self, value):
        self._tables_in = value

    @property
    def table_out(self):
        return self._table_out

    @table_out.setter
    def table_out(self, value):
        self._table_out = value

    @property
    def sql(self):
        return self._sql

    @sql.setter
    def sql(self, value):
        self._sql = value

    @property
    def del_table(self):
        return self._del_table

    @del_table.setter
    def del_table(self, value):
        self._del_table = value

    @property
    def out_many(self):
        return self._out_many

    @out_many.setter
    def out_many(self, value):
        self._out_many = value

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        self._method = value

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









