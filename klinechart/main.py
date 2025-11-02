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
from model.kline import KLine
from algo.zigzag import OnCalculate
from algo.weibi import get_weibi_list
from callback.call_back import *
import logging

def calc_zig_zag(klines: List[KLine]):
    zig_zag = OnCalculate(klines)
    return zig_zag
# -*- coding: utf-8 -*-
import os
import sys
from PySide6 import QtWidgets

# keep compatibility with PyQt if it was imported earlier
if "PyQt5" in sys.modules:
    del sys.modules["PyQt5"]

# ensure parent dir is on path (keeps previous behavior)
work_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(work_dir)


def main():
    """Thin entrypoint: construct QApplication and show main window from gui module."""
    app = QtWidgets.QApplication(sys.argv)
    from klinechart.gui import MainWindow
    w = MainWindow()
    w.resize(1024, 768)
    w.show()
    app.exec()


if __name__ == '__main__':
    main()