"""GUI module containing MainWindow. Keeps window/UI code separate from entrypoint."""
from PySide6 import QtWidgets
from typing import Dict
from klinechart.chart import ChartWidget, ChartVolume, ChartCandle, ChartMacd, \
    ChartArrow, ChartLine, ChartStraight, ChartSignal, ItemIndex
from klinechart.chart.object import PlotIndex, PlotItemInfo, ChartItemInfo
from klinechart.trader.config import conf
from algo.weibi import get_weibi_list
from .app_model import AppModel


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # create model and load data
        model = AppModel(conf)
        model.load()
        datas: Dict[PlotIndex, PlotItemInfo] = model.get_datas()

        widget = ChartWidget(self)
        # seed manager's history klines from first plot/item
        widget.manager.update_history_klines(datas[PlotIndex(0)][ItemIndex(0)].bars.values())
        # let model run algos using manager.klines
        model.apply_algos(widget.manager.klines)
        # prepare weibis if callbacks need them

        plots = conf["plots"]
        for plot_index, plot in enumerate(plots):
            if plot_index != len(plots) - 1:
                axis = True
            else:
                axis = False
            # The `widget` in the code is an instance of `ChartWidget` being used to create a main
            # window for a GUI application. Here is a breakdown of what `widget` is doing in the code
            # snippet:
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
                    raise RuntimeError("not match item")

        widget.add_cursor()
        widget.update_all_history_data(datas)

        self.graphWidget = widget
        self.setCentralWidget(self.graphWidget)
