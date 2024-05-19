# -*- coding: utf-8 -*
"""
@file: kline.py
@author: luhx
@description: K线数据元素
"""
from datetime import datetime
from enum import Enum


class KLine:
    def __init__(self, time=0, open=0, high=0, low=0, close=0, volume=0, symbol=""):
        self.time = time
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume
        self.symbol = symbol  # 合约号

    def __str__(self):
        return "t:{},o:{},h:{},l:{},c:{},v:{}".\
            format(str(datetime.fromtimestamp(self.time)),
                   self.open, self.high, self.low, self.close, self.volume)

    def __repr__(self):
        return self.__str__()


class KSide(Enum):
    INITIAL = 0
    UP = 1
    DOWN = -1


class stCombineK:
    def __init__(self, data, begin, end, base, isup):
        self.data: KLine = data     # K线数据
        self.pos_begin: int = begin      # 起始
        self.pos_end: int = end          # 结束
        self.pos_extreme: int = base     # 最高或者最低位置,极值点位置
        self.isUp: KSide = KSide(isup)            # 是否向上

    def __str__(self):
        up = "up" if self.isUp else "down"
        return "[{}]:begin:{},end:{},base:{}".format(up, self.pos_begin, self.pos_end, self.pos_extreme)

    def __repr__(self):
        return self.__str__()