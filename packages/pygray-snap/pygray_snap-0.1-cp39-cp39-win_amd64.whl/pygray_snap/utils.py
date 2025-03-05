import json
import os
import random

_path = os.path.dirname(__file__) + os.sep + "ua.jsonl"


def load():
    uas = []
    with open(_path, encoding="utf-8") as fp:
        for jstr in fp:
            o = json.loads(jstr)
            uas.append(o)

    return uas


class UaList:
    ins = None

    def __new__(cls, *args, **kwargs):
        if cls.ins is None:
            obj = super().__new__(cls)
            cls.ins = obj
            return obj

        return cls.ins

    def __init__(self, uas):
        self.uas = uas

    def get(self):
        d = random.choice(self.uas)
        return d.get("useragent")


class UserAgent:
    uas = None
    o = None

    def __new__(cls, *args, **kwargs):
        if cls.uas is None:
            obj = super().__new__(cls)
            cls.uas = load()
            cls.o = obj
            return obj

        return cls.o

    def get(self):
        return UaList(self.uas).get()
