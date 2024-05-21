# -*- coding: utf-8 -*-
"""
@author: <luhx>
@desc: 根据逻辑实现的缠论的笔
包含的处理：1 确定方向：如果第n根K线发生包含关系，找到第n-1根K线，此两根K线没有包含关系，且n-1及其之前的包含关系都处理完毕。
如果第n-1根K线到第n根K线，高点抬高，则方向为向上，反之，如果低点降低，则方向为向下。
2 合并K线：2根有包含关系的K线，如果方向向下，则取其中高点中的低点作为新K线高点，取其中低点中的低点作为新K线低点，由此合并出一根新K线。
如果方向向上，则取其中高点中的高点作为新K线高点，取其中低点中的高点作为新K线低点，由此合并出一根新K线。
"""
from model.kline import KLine, stCombineK, KSide
from typing import List, Any
from chanlun.float_compare import *
from copy import copy


def _Cal_MERGE(combs: List[stCombineK]) -> int:
    """
    合并K线逻辑,接受一个stCombineK类型的列表combs, 返回一个整数值表示独立K线的个数
    :param klines:
    :return:
    """
    size = len(combs)
    if len(combs) < 2:    # <=2时，返回本身的长度
        return size

    pBegin = 0      # 起始位置
    pLast = pBegin  # 最后一个独立K线的位置
    pPrev = pBegin  # 前一个独立K线的位置
    pCur = pBegin + 1           # 当前K线的位置
    pEnd = pBegin + size - 1    # 最后一个K线位置
    bUp = KSide.INITIAL         # 方向标志，初始化为 KSide.INITIAL

    def IndependentK(combs: List[stCombineK], b_up: KSide):
        """用于处理独立K线的情况，更新标志和指针，并进行值的拷贝"""
        nonlocal bUp
        nonlocal pPrev
        nonlocal pLast
        bUp = b_up
        pPrev = pCur
        pLast += 1  # 每处理一根独立K线，pLast增加1
        combs[pLast] = copy(combs[pCur])    # 值的拷贝，而不是指针, 总是拷贝第一个
        return

    def ContainsK(combs: List[stCombineK], low, high, index, pos_end):
        """用于处理包含K线的情况，更新K线的数据和位置"""
        nonlocal pPrev
        combs[pLast].data.low = low
        combs[pLast].data.high = high
        combs[pLast].pos_end = pos_end
        combs[pLast].pos_extreme = index
        pPrev = pLast
        return

    # 初始合并逻辑
    if greater_than_0(combs[pCur].data.high - combs[pPrev].data.high) and \
        greater_than_0(combs[pCur].data.low - combs[pPrev].data.low):
        # 高点升，低点也升, 向上
        IndependentK(combs, KSide.UP)
    elif less_than_0(combs[pCur].data.high - combs[pPrev].data.high) and \
        less_than_0(combs[pCur].data.low - combs[pPrev].data.low):
        # 高点降，低点也降，向下
        IndependentK(combs, KSide.DOWN)
    else:
        if greater_than_0(combs[pCur].data.high - combs[pPrev].data) or \
            less_than_0(combs[pCur].data.low - combs[pPrev].data.low):
            # 高点高于前 或是 低点低于前， 右包含，向上合并
            ContainsK(combs, combs[pPrev].data.low, combs[pCur].data.high, combs[pCur].pos_begin, combs[pCur].pos_begin)
        else:   # 左包函，即低点高于前，高点低于前，也向上合并
            ContainsK(combs, combs[pCur].data.low, combs[pPrev].data.high, combs[pPrev].pos_begin, combs[pCur].pos_begin)

    while pCur <= pEnd:
        if greater_than_0(combs[pCur].data.high - combs[pPrev].data.high) and \
                greater_than_0(combs[pCur].data.low - combs[pPrev].data.low):
            IndependentK(combs, KSide.UP)
        elif less_than_0(combs[pCur].data.high - combs[pPrev].data.high) and \
                less_than_0(combs[pCur].data.low - combs[pPrev].data.low):
            IndependentK(combs, KSide.DOWN)
        else:
            # 包含
            if greater_than_0(combs[pCur].data.high - combs[pPrev].data.high) or \
                    less_than_0(combs[pCur].data.low - combs[pPrev].data.low):
                    # 右包含
                if bUp.UP:    # 向上，一样高取左极值，不一样高肯定是右高，取右值
                    pos_index = combs[pPrev].pos_extreme if equ_than_0(combs[pCur].data.high - combs[pPrev].data.high) else combs[pCur].pos_begin
                    ContainsK(combs[pPrev].data.low, combs[pCur].data.high, pos_index, combs[pCur].pos_begin)
                else:         # 向下，一样低取左极值，不一样低肯定是右低，取右值
                    pos_index = combs[pPrev].pos_extreme if equ_than_0(combs[pCur].data.low - combs[pPrev].data.low) else combs[pCur].pos_begin
                    ContainsK(combs[pCur].data.low, combs[pPrev].data.high, pos_index, combs[pCur].pos_begin)
            else:   # 左包含
                if bUp.UP:  # 向上，一样高取左极值，否则高肯定是右高，取右值
                    pos_index = combs[pPrev].pos_extreme if equ_than_0(combs[pPrev].data.high - combs[pCur].data.high) else combs[pCur].pos_begin
                    ContainsK(combs[pCur].data.low, combs[pPrev].data.high, pos_index, combs[pCur].pos_begin)
                else:       # 向下，一样低取左极值，否则低肯定是右低，取右值
                    pos_index = combs[pPrev].pos_extreme if equ_than_0(combs[pPrev].data.low - combs[pCur].data.low) else combs[pCur].pos_begin
                    ContainsK(combs[pPrev].data.low, combs[pCur].data.high, pos_index, combs[pCur].pos_begin)
        pCur += 1
    return pLast - pBegin + 1   # 得出独立K线的数量
