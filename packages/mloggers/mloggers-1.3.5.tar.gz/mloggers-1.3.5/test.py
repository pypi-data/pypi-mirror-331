from dataclasses import dataclass
from enum import Enum

from mloggers import ConsoleLogger, FileLogger, LogLevel


class MyEnum(Enum):
    A = 1
    B = 2
    C = 3


@dataclass
class SomeObject:
    a: int
    b: str


@dataclass
class SomeJSONObject:
    c: float
    d: bool

    def to_json(self):
        return {"c": self.c, "d": self.d}


# logger = FileLogger("test.log", default_priority=LogLevel.DEBUG)
logger = ConsoleLogger(default_priority=LogLevel.DEBUG)
logger.info("Hello, world!")
o1 = SomeObject(1, "hello")
o2 = SomeJSONObject(1.0, True)
logger.error("This is an error message.")
logger.error(2)
logger.error(2.532535)
logger.error(False)
logger.warn(o1)
logger.warn(o2)
logger.warn(MyEnum.B)
logger.debug(
    {
        "a": 1,
        "b": "hello",
        "object": o1,
        "json_object": o2,
    }
)
logger.debug(
    {
        "a": 1,
        "b": True,
        "c": 1.27453,
        "object": o1,
        "json_object": o2,
        "enum": MyEnum.A,
    }
)
