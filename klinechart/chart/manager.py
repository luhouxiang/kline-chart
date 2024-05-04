# -*- coding: utf-8 -*-
"""K线序列数据管理工具
"""
from typing import Dict, Tuple

from .object import PlotItemInfo
from .object import PlotIndex, ItemIndex, ChartItemInfo, MinMaxIdxTuple, MinMaxPriceTuple

from .base import to_int
from model.kline import KLine
from datetime import datetime
from utils.user_logbook import user_log as logger


class BarManager:
    """"""

    def __init__(self):
        """"""
        self._datetime_index_map: Dict[datetime, int] = {}
        self._index_datetime_map: Dict[int, datetime] = {}

        self._all_chart_infos: Dict[PlotIndex, PlotItemInfo] = {}
        self._all_ranges: Dict[PlotIndex, Dict[MinMaxIdxTuple, MinMaxPriceTuple]] = {}
        self.klines: list[KLine] = []

    def update_history_klines(self, bars):
        for v in bars:
            k: KLine = KLine()
            k.time = v[0].timestamp()
            k.open = v[1]
            k.high = v[2]
            k.low = v[3]
            k.close = v[4]
            k.volume = v[5]
            self.klines.append(k)
        logger.info(f"klines.size={len(self.klines)}")


    def update_history_data(self, plot_index: PlotIndex, chart_index: ItemIndex, info: ChartItemInfo) -> None:
        """
        设置历史数据
        """
        if plot_index not in self._all_chart_infos:
            self._all_chart_infos[plot_index] = {}
        self._all_chart_infos[plot_index][chart_index] = info
        if plot_index == 0 and chart_index == 0:
            ix_list = range(len(info.bars))
            dt_list = info.bars.keys()
            self._datetime_index_map = dict(zip(dt_list, ix_list))
            self._index_datetime_map = dict(zip(ix_list, dt_list))

    def get_count(self) -> int:
        """
        Get total number of bars.
        """
        return len(self._all_chart_infos[0][0].bars)

    def get_index(self, dt: datetime) -> int:
        """
        Get index with datetime.
        """
        return self._datetime_index_map.get(dt, None)

    def get_datetime(self, ix: float) -> datetime:
        """
        Get datetime with index.
        """
        ix = to_int(ix)
        return self._index_datetime_map.get(ix, None)

    def get_layout_range(self, layout_index: int, min_ix: float = None, max_ix: float = None) -> Tuple[float, float]:
        if layout_index not in self._all_chart_infos:
            return 0, 1
        if not min_ix:
            min_ix = 0
            if max_ix:
                max_ix = to_int(max_ix)
            else:
                max_ix = len(self._all_chart_infos[layout_index][0].bars) - 1
        else:
            min_ix = to_int(min_ix)
            max_ix = to_int(max_ix)
            max_ix = min(max_ix, len(self._all_chart_infos[layout_index][0].bars))  # TODO: 不减1？

        if layout_index not in self._all_ranges:
            self._all_ranges[layout_index] = {}
        buf = self._all_ranges[layout_index].get((min_ix, max_ix), None)
        if buf:
            return buf

        max_price = float("-inf")  # 无限小，比所有数都小
        min_price = float("inf")  # 无限大，比所有数都大
        chart_items: dict[ItemIndex, ChartItemInfo] = self._all_chart_infos[layout_index]
        for info in chart_items.values():
            if not info.bars:
                continue
            bar_list = list(info.bars.values())[min_ix:max_ix + 1]

            if info.type == "Arrow":
                continue  # 对于画箭头型的，大小不在区域范围内
            elif info.type == "Straight":
                continue  # 对于画直线，依附于K线图，大小不在区域范围内
            elif info.type == "Candle":
                for bar in bar_list[:]:
                    for item in bar[1:-1]:
                        max_price = max(max_price, item)
                        min_price = min(min_price, item)
            else:
                for bar in bar_list[:]:
                    for item in bar[1:]:
                        max_price = max(max_price, item)
                        min_price = min(min_price, item)
        if min_price == float("inf"):
            min_price = 0
        if max_price == float("-inf"):
            max_price = 1
        self._all_ranges[layout_index][(min_ix, max_ix)] = (min_price, max_price)
        return min_price, max_price
