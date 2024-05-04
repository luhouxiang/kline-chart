# -*- coding: utf-8 -*-
"""
Created on
@author: <NAME>
@file: call_back.py
@desc: 由配置文件回调过程
"""
from model.kline import KLine
from algo.formula import MA
from datetime import datetime
from algo.weibi import get_weibi_list
from utils.user_logbook import user_log as logger
from typing import List, Any
from model.obj import Direction
from chanlun.bi import Cal_OLD_TEST


def fn_calc_ma20_60(klines: list[KLine]):
    """由配置文件回调ma20,ma60的计算过程"""
    bars = {}
    MA20, MA60 = MA(20), MA(60)
    for k in klines:
        dt = datetime.fromtimestamp(k.time)
        MA20.input(k.close)
        MA60.input(k.close)
        bars[dt] = [dt, MA20.ma, MA60.ma]
    return bars


def fn_calc_wei_bi(klines: list[KLine]) -> List[Any]:
    """回调计算过程"""
    wbs = get_weibi_list(klines, N=5)
    logger.info(wbs)
    items = []
    for w in wbs:
        p1 = w.low if w.direction == Direction.Up else w.high
        p2 = w.high if w.direction == Direction.Up else w.low
        items.append([w.sdt, p1, w.edt, p2, 0])
    return items

def fn_calc_bi(klines: list[KLine]) -> List[Any]:
    pass
    # Cal_OLD_TEST(klines)



