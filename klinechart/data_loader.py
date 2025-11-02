"""Data loading utilities extracted from main to keep concerns separated."""
from typing import Dict, List
import logging
from utils import file_txt
from klinechart.chart.object import ChartItemInfo, PlotIndex, ItemIndex, BarDict, DataItem


def calc_bars(data_list, data_type: List[str]) -> BarDict:
    """Convert text lines to BarDict used by charts."""
    bar_dict: BarDict = {}
    for data_index, txt in enumerate(data_list):
        bar = DataItem(txt, data_type)
        if bar:
            bar_dict[bar[0]] = bar
    return bar_dict


def load_data(conf: Dict[str, any]) -> Dict[PlotIndex, Dict[ItemIndex, ChartItemInfo]]:
    """
    Load files described in config and return a mapping PlotIndex -> (ItemIndex -> ChartItemInfo)
    """
    local_data: Dict[PlotIndex, Dict[ItemIndex, ChartItemInfo]] = {}
    plots = conf["plots"]
    for plot_index, plot in enumerate(plots):
        plot_info: Dict[ItemIndex, ChartItemInfo] = {}
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
            logging.info(f"file_name: {item['file_name']}")
            logging.info(f"plot_index:{plot_index}, item_index:{item_index}, len(bar_dict)={len(bar_dict)}")
        local_data[PlotIndex(plot_index)] = plot_info

    return local_data
