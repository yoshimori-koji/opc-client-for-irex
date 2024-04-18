import enum


class Status(enum.IntEnum):
    STOP = 0
    RUN = 1
    ERROR = 2
    SETUP = 3


class Error(enum.IntEnum):
    NOTHING = 0
    POWER = 1
    MECHANICAL = 2
    POWER_AND_MECHANICAL = 3
    OPERATION = 4
    POWER_AND_OPERATION = 5
    MECHANICAL_AND_OPERATION = 6
    ALL = 7
