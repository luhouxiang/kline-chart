"""Data loading utilities extracted from main to keep concerns separated."""
from typing import Dict, List, Tuple, Optional
import logging
from klinechart.myutils import file_txt
from klinechart.chart.object import ChartItemInfo, PlotIndex, ItemIndex, BarDict, DataItem
from pathlib import Path
import os
from datetime import datetime
from collections import OrderedDict


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


def extract_file_metadata(file_path: str) -> Tuple[str, str, str]:
    """Read the first descriptive line of a data file to capture symbol/name/period."""
    symbol = ""
    name = ""
    period = ""

    if not file_path or not os.path.exists(file_path):
        return symbol, name, period

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                # skip if line looks like data (starts with digit) or like CSV header
                if line[0].isdigit() or ',' in line:
                    break
                tokens = line.replace('\t', ' ').split()
                if not tokens:
                    continue
                symbol = tokens[0]
                if len(tokens) > 1:
                    name = tokens[1]
                if len(tokens) > 2:
                    period = tokens[2]
                break
    except Exception:
        logging.debug("Failed parsing metadata from %s", file_path)

    return symbol, name, period


def _parse_window_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    text = text.replace('/', '-')
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M"
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    logging.warning("Unrecognized datetime format for data_window value: %s", value)
    return None


def _normalize_count(value) -> Optional[int]:
    if value is None:
        return None
    try:
        count = int(value)
    except (TypeError, ValueError):
        return None
    return count if count > 0 else None


def _select_datetimes(sorted_dts: List[datetime],
                      start_dt: Optional[datetime],
                      end_dt: Optional[datetime],
                      count: Optional[int]) -> List[datetime]:
    if not sorted_dts:
        return []

    total = len(sorted_dts)

    def first_ge(target: datetime) -> int:
        for idx, dt in enumerate(sorted_dts):
            if dt >= target:
                return idx
        return total

    def last_le(target: datetime) -> int:
        for idx in range(total - 1, -1, -1):
            if sorted_dts[idx] <= target:
                return idx
        return -1

    if start_dt and end_dt:
        left = first_ge(start_dt)
        right = last_le(end_dt)
        if left >= total or right < 0 or right < left:
            return []
        return sorted_dts[left:right + 1]

    if start_dt:
        left = first_ge(start_dt)
        if left >= total:
            return []
        if count:
            return sorted_dts[left: left + count]
        return sorted_dts[left:]

    if end_dt:
        right = last_le(end_dt)
        if right < 0:
            return []
        if count:
            start = max(0, right - count + 1)
            return sorted_dts[start: right + 1]
        return sorted_dts[: right + 1]

    if count:
        return sorted_dts[-count:]

    return sorted_dts[:]


def _apply_data_window(local_data: Dict[PlotIndex, Dict[ItemIndex, ChartItemInfo]],
                       window_cfg: Optional[Dict]) -> None:
    if not window_cfg:
        return
    plot0 = local_data.get(PlotIndex(0))
    if not plot0:
        return
    first_item = plot0.get(ItemIndex(0))
    if not first_item or not first_item.bars:
        return

    start_dt = _parse_window_datetime(window_cfg.get("start"))
    end_dt = _parse_window_datetime(window_cfg.get("end"))
    count = _normalize_count(window_cfg.get("count"))

    base_datetimes = sorted(first_item.bars.keys())
    selected = _select_datetimes(base_datetimes, start_dt, end_dt, count)

    if not selected:
        logging.warning("data_window produced no candles; keeping original data set.")
        return

    selected_set = set(selected)
    for plot_info in local_data.values():
        for info in plot_info.values():
            if not info.bars:
                continue
            ordered = OrderedDict()
            for dt in selected:
                if dt in info.bars:
                    ordered[dt] = info.bars[dt]
            info.bars = ordered


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
            if item_info.type == "Candle":
                symbol, name, period = extract_file_metadata(data_path)
                item_info.symbol_code = symbol
                item_info.symbol_name = name
                item_info.symbol_period = period
            item_info.bars = bar_dict
            plot_info[ItemIndex(item_index)] = item_info
            logging.info(f"file_name: {item['file_name']}")
            logging.info(f"plot_index:{plot_index}, item_index:{item_index}, len(bar_dict)={len(bar_dict)}")
        local_data[PlotIndex(plot_index)] = plot_info

    _apply_data_window(local_data, conf.get("data_window"))

    return local_data
