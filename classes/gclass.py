"""
@author: António Brito / Carlos Bragança
(2025) objective: Generic class
"""
# Generic Class
import sys
import datetime
from sqlalchemy import create_engine, text

class Gclass:
    def __init__(self):
        pass

    @classmethod
    def from_string(cls, str_data):
        str_list = str_data.split(";")
        strarg = 'cls(str_list[0]'
        for i in range(1, len(str_list)):
            strarg += ',str_list[' + str(i) + ']'
        strarg += ')'
        return eval(strarg)

    @classmethod
    def reset(cls):
        cls.obj = dict()
        cls.lst = list()
        cls.pos = 0

    @classmethod
    def get_id(cls, id):
        id = int(id)
        if id == 0:
            if len(cls.lst) == 0:
                id = 1
            else:
                id = max(cls.lst) + 1
        return id

    @classmethod
    def getlines(cls, att, value):
        return [obj.id for obj in list(cls.obj.values()) if getattr(obj, att) == value]

    @classmethod
    def next(cls):
        cls.pos += 1
        return cls.current()

    @classmethod
    def previous(cls):
        cls.pos -= 1
        return cls.current()

    @classmethod
    def current(cls, code = None):
        if code in cls.lst:
            cls.pos = cls.lst.index(code)
        if cls.pos < 0:
            cls.pos = 0
            return None
        elif cls.pos >= len(cls.lst):
            cls.pos = len(cls.lst) - 1
            return None
        else:
            code = cls.lst[cls.pos]
            return cls.obj[code]

    @classmethod
    def first(cls):
        cls.pos = 0
        return cls.current()

    @classmethod
    def last(cls):
        cls.pos = len(cls.lst) - 1
        return cls.current()

    @classmethod
    def remove(cls, p):
        obj = cls.obj[p]
        id = cls.att[0][1:]
        command = f'DELETE FROM {cls.__name__} WHERE {id}={cls.conv(obj,id,p)}'
        cls.sqlexe(command)
        cls.lst.remove(p)
        del cls.obj[p]

    @classmethod
    def insert(cls, p):
        obj = cls.obj[p]
        command = f'INSERT INTO {cls.__name__} VALUES('
        for att in cls.att:
            value = getattr(obj, att)
            command += f'{cls.conv(obj, att, value)},'
        command = command[:-1] + ")"
        cls.sqlexe(command)

    @classmethod
    def update(cls, p):
        obj = cls.obj[p]
        command = f'UPDATE "{cls.__name__}" SET'
        for att in cls.att[1:]:
            value = getattr(obj, att)
            command += f' {att[1:]} = {cls.conv(obj, att, value)},'
        id = cls.att[0][1:]
        command = command[:-1] + f' WHERE {id} = {cls.conv(obj, id, p)}'
        print(command)
        cls.sqlexe(command)

    @staticmethod
    def conv(obj, att, value):
        v = getattr(obj, att)
        if type(v) == str or type(v) == datetime.date:
            ret = f'"{value}"'
        else:
            ret = f'{value}'
        return ret

    @classmethod
    def orderfunc(cls, e):
        return getattr(cls.obj[e], cls.sortkey)

    @classmethod
    def sort(cls, att, reverse = False):
        cls.sortkey = att
        cls.lst.sort(key=cls.orderfunc, reverse= reverse)

    @classmethod
    def find(cls, value, att):
        lobj = cls.obj.values()
        fobj = [obj for obj in lobj if getattr(obj, att) == value]
        return fobj

    @classmethod
    def set_filter(cls, f_dic = {}):
        if f_dic:
            code = cls.att[0]
            lobj = cls.obj.values()
            s = set()
            for att,listf in f_dic.items():
                s1 = set([getattr(obj, code) for obj in lobj if getattr(obj, att) in listf])
                s = s.union(s1)
            if len(s) > 0:
                cls.lst = list(s)
                cls.pos = 0
        else:
            obj = cls.current()
            cls.lst = list(cls.obj.keys())
            code = cls.att[0]
            cls.current(getattr(obj, code))

    @classmethod
    def getatlist(cls, att):
        return [getattr(obj, att) for obj in list(cls.obj.values())]

    @classmethod
    def read(cls, path = ''):
        cls.obj = dict()
        cls.lst = list()
        cls.path = path
        try:
            # Test if file exists
            import os
            if not os.path.exists(path):
                print(f"ERROR: {path} data file not found")
                return
            # Use SQLAlchemy to connect
            engine = create_engine(f'sqlite:///{path}')
            tname = cls.__name__
            with engine.connect() as conn:
                # Check if table exists
                result = conn.execute(
                    text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tname}'")
                )
                table = result.fetchone()
                if table is None or table[0] != tname:
                    print(f"ERROR: table {tname} missing in database {path}")
                    sys.exit()
                # Read all rows
                result = conn.execute(text(f"SELECT * FROM {tname}"))
                rows = result.fetchall()
                if rows:
                    for r in rows:
                        objstr = f'{r[0]}'
                        for att in range(1, len(r)):
                            objstr += f';{r[att]}'
                        cls.from_string(objstr)
        except Exception as err:
            print(f"Error in read method:\n{err}\n{type(err)}")
            sys.exit()

    def __str__(self):
        strprint = "f'"
        for att in type(self).att:
            strprint += '{self.' + att + '};'
        strprint = strprint[:-1] + "'"
        return eval(strprint)

    @classmethod
    def sqlexe(cls, command):
        resul = None
        try:
            engine = create_engine(f'sqlite:///{cls.path}')
            tname = cls.__name__
            with engine.connect() as conn:
                # Check if table exists
                result = conn.execute(
                    text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tname}'")
                )
                table = result.fetchone()
                if table is None or table[0] != tname:
                    print(f"ERROR: table {tname} missing in database {cls.path}")
                    sys.exit()
                # Execute the command
                result = conn.execute(text(command))
                try:
                    resul = result.fetchall()
                except Exception:
                    resul = None
                conn.commit()
        except Exception as er:
            print(f'sqlalchemy error: {er}')
        return resul
