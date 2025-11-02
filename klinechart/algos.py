"""Algorithm glue: wrappers to run algos and populate plot data structures.

This module isolates algorithm-related processing so UI code doesn't directly call algos.
"""
from typing import Dict, List
from klinechart.chart import PlotIndex, PlotItemInfo, ChartItemInfo, ItemIndex
from model.kline import KLine
import callback.call_back as cb
from algo.zigzag import OnCalculate


def calc_zig_zag(klines: List[KLine]):
    """Thin wrapper for zigzag calculation."""
    zig_zag = OnCalculate(klines)
    return zig_zag


def obtain_data_from_algo(klines: list[KLine], data: Dict[PlotIndex, PlotItemInfo]):
    """Populate ChartItemInfo entries by calling configured callback functions.

    This replaces the old use of globals() and explicitly resolves functions from
    callback.call_back module.
    """
    # run any global algo pre-calculations
    calc_zig_zag(klines)
    for plot_index in data.keys():
        plot_item_info: PlotItemInfo = data[plot_index]
        for item_index in plot_item_info:
            info: ChartItemInfo = plot_item_info[item_index]
            if not info.bars and info.func_name:
                func = getattr(cb, info.func_name, None)
                if not func:
                    # skip silently if function not found; caller can log/handle
                    continue
                if info.type == "Straight":
                    info.discrete_list = func(klines)
                else:
                    info.bars = func(klines)
