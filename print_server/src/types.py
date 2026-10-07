from enum import StrEnum


class Environment(StrEnum):
    DEV = "DEV"
    PROD = "PROD"


class Dictify:
    def to_dict(self):
        _dict = self.__dict__.copy()
        return _dict
