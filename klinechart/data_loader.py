"""Data loading utilities extracted from main to keep concerns separated."""
from typing import Dict, List
import logging
from utils import file_txt
from klinechart.chart.object import ChartItemInfo, PlotIndex, ItemIndex, BarDict, DataItem
from pathlib import Path
import os


def calc_bars(data_list, data_type: List[str]) -> BarDict:
    """Convert text lines to BarDict used by charts."""
    bar_dict: BarDict = {}
    def normalize_line(txt: str) -> str:
        """Normalize different input line formats into a CSV of:
        dt(YYYY-MM-DD HH:MM:SS), open, high, low, close, volume
        Returns an empty string if normalization fails.
        """
        if not txt:
            return ""
        parts = [p.strip() for p in txt.split(',')]
        if not parts:
            return ""

        # Format A: split date and time fields, e.g. '2024/04/11,1350,6490,6491,6481,6483,11267,...'
        if '/' in parts[0] and len(parts) >= 7 and parts[1].isdigit():
            date_part = parts[0].replace('/', '-')
            time_part = parts[1].zfill(4)
            hh = time_part[:2]
            mm = time_part[2:]
            dt = f"{date_part} {hh}:{mm}:00"
            # open, high, low, close, volume are next 5 tokens
            nums = parts[2:2+5]
            if len(nums) < 5:
                return ""
            return ','.join([dt] + nums)

        # Format B: existing candle format: 'YYYY-.. HH:MM:SS,open,high,low,close,volume'
        # Just keep first 6 fields
        if (' ' in parts[0] or '-' in parts[0]) and len(parts) >= 6:
            return ','.join(parts[:6])

        # Fallback: if there are at least 6 tokens, take first 6
        if len(parts) >= 6:
            return ','.join(parts[:6])

        return ""

    for data_index, txt in enumerate(data_list):
        norm = normalize_line(txt)
        if not norm:
            continue
        bar = DataItem(norm, data_type)
        if bar:
            try:
                bar_dict[bar[0]] = bar
            except Exception:
                # if keying by bar[0] fails (unexpected type), skip
                continue
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
            # Resolve file path relative to repository root (two levels up from this file)
            file_name = item.get("file_name", "")
            if file_name:
                if not os.path.isabs(file_name):
                    repo_root = Path(__file__).resolve().parent.parent
                    # Interpret relative paths in config relative to the `etc` directory
                    config_dir = repo_root.joinpath('etc')
                    candidate = config_dir.joinpath(file_name).resolve()
                    # If candidate doesn't exist, try interpreting file_name as-is
                    if candidate.exists():
                        data_path = str(candidate)
                    else:
                        data_path = file_name
                else:
                    data_path = file_name
            else:
                data_path = file_name

            data_list = file_txt.read_file(data_path)
            bar_dict: BarDict = calc_bars(data_list, item_info.data_type)
            item_info.bars = bar_dict
            plot_info[ItemIndex(item_index)] = item_info
            logging.info(f"file_name: {item['file_name']}")
            logging.info(f"plot_index:{plot_index}, item_index:{item_index}, len(bar_dict)={len(bar_dict)}")
        local_data[PlotIndex(plot_index)] = plot_info

    return local_data
