# -*- coding: utf-8 -*-
import os
import sys
from PySide6 import QtWidgets
from datetime import datetime
if "PyQt5" in sys.modules:
    del sys.modules["PyQt5"]
work_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print("work_dir: ", work_dir)
sys.path.append(work_dir)
from typing import Dict, List
from klinechart.chart import ChartWidget, ChartVolume, ChartCandle, ChartMacd,\
    ChartArrow, ChartLine, ChartStraight, ChartSignal, ItemIndex
from klinechart.chart.object import DataItem
from klinechart.chart import PlotIndex, BarDict, PlotItemInfo, ChartItemInfo
from klinechart.trader.config import conf
from utils import file_txt
from utils.user_logbook import user_log as logger, init_logger
from model.kline import KLine
from algo.zigzag import OnCalculate
from algo.weibi import get_weibi_list
from callback.call_back import fn_calc_ma20_60, fn_calc_wei_bi, fn_calc_bi


def calc_zig_zag(klines: List[KLine]):
    zig_zag = OnCalculate(klines)
    return zig_zag


def calc_volumes(klines: list[KLine]):
    bars = {}
    for k in klines:
        dt = datetime.fromtimestamp(k.time)
        bars[dt] = [dt, k.volume]
    return bars


def obtain_data_from_algo(klines: list[KLine], data: Dict[PlotIndex, PlotItemInfo]):
    calc_zig_zag(klines)
    for plot_index in data.keys():
        plot_item_info:PlotItemInfo = data[plot_index]
        for item_index in plot_item_info:
            info: ChartItemInfo = plot_item_info[item_index]
            if not info.bars and info.func_name:
                if info.type == "Straight":
                    info.discrete_list = globals()[info.func_name](klines)
                else:
                    info.bars = globals()[info.func_name](klines)


def load_data(conf: Dict[str, any]) -> Dict[PlotIndex, PlotItemInfo]:
    """
    返回以layout_index, index为key的各item的kl_data_list
    """
    local_data: Dict[PlotIndex, PlotItemInfo] = {}
    plots = conf["plots"]
    for plot_index, plot in enumerate(plots):
        plot_info: PlotItemInfo = {}
        for item_index, item in enumerate(plot["chart_item"]):
            item_info: ChartItemInfo = ChartItemInfo()
            item_info.type = item["type"]
            item_info.params = item["params"] if "params" in item else []
            item_info.func_name = item["func_name"] if "func_name" in item else ""
            item_info.data_type = item["data_type"] if "data_type" in item else []
            data_list = file_txt.read_file(item["file_name"])
            bar_dict: BarDict = calc_bars(data_list, item_info.data_type)
            item_info.bars = bar_dict
            plot_info[ItemIndex(item_index)] = item_info
            logger.info(F"file_name: {item['file_name']}")
            logger.info(F"plot_index:{plot_index}, item_index:{item_index}, len(bar_dict)={len(bar_dict)}")
        local_data[PlotIndex(plot_index)] = plot_info

    return local_data


def calc_bars(data_list, data_type: List[str]) -> BarDict:
    bar_dict: BarDict = {}
    for data_index, txt in enumerate(data_list):
        bar = DataItem(txt, data_type)
        if bar:
            bar_dict[bar[0]] = bar
    return bar_dict


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        datas: Dict[PlotIndex, PlotItemInfo] = load_data(conf)
        widget = ChartWidget()
        widget.manager.update_history_klines(datas[PlotIndex(0)][ItemIndex(0)].bars.values())
        obtain_data_from_algo(widget.manager.klines, datas)
        weibis = get_weibi_list(widget.manager.klines)

        plots = conf["plots"]
        for plot_index, plot in enumerate(plots):
            if plot_index != len(plots) - 1:
                axis = True
            else:
                axis = False
            widget.add_plot(hide_x_axis=axis, maximum_height=plots[plot_index]["max_height"])  # plot
            for index, chart_item in enumerate(plot["chart_item"]):
                if chart_item["type"] == "Candle":
                    widget.add_item(plot_index, ChartCandle)
                elif chart_item["type"] == "Volume":
                    widget.add_item(plot_index, ChartVolume)
                elif chart_item["type"] == "Line":  # 曲线
                    widget.add_item(plot_index, ChartLine)
                elif chart_item["type"] == "Macd":
                    widget.add_item(plot_index, ChartMacd)
                elif chart_item["type"] == "Arrow":
                    widget.add_item(plot_index, ChartArrow)
                elif chart_item["type"] == "Straight":  # 直线
                    widget.add_item(plot_index, ChartStraight)
                elif chart_item["type"] == "Signal":
                    widget.add_item(plot_index, ChartSignal)
                else:
                    raise "not match item"

        widget.add_cursor()
        widget.update_all_history_data(datas)

        self.graphWidget = widget
        self.setCentralWidget(self.graphWidget)


if __name__ == '__main__':
    init_logger("info")
    logger.info(conf)

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resize(1024, 768)
    w.show()
    app.exec()