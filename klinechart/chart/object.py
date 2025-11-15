"""
Basic data structure used for general trading function in the trading platform.
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Dict, NewType, Tuple
from enum import Enum


TIndex = int


class DataItem(list):
    """ 表格数据
    如果输入数据类似如下：‘2022/01/14 2216,4625.0,4626.0,4621.0,4622.0’
    我们将其转换为：[2022-01-14 22:16:00, 4625.0, 4626.0, 4621.0, 4622.0]
    如果输入数据如下：‘2022-01-14 22:16:00,4622.0’
    我们将其转换为：['2022-01-14 22:16:00', 4622.0]
    """

    def __init__(self, txt="", data_type=[]):
        list.__init__([])
        self.init_txt(txt, data_type)

    def init_txt(self, txt, data_type=[]):
        if not txt:
            return
        arr = txt.split(",")
        # Handle multiple timestamp formats:
        # 1) Single-field datetime: 'YYYY-MM-DD HH:MM:SS,...' (original format)
        # 2) Split date and time fields: 'YYYY/MM/DD,1350,...' where the second field is HHMM
        if not data_type:
            # Try to normalize the first one or two fields into a single datetime object
            try:
                if len(arr) >= 2 and arr[0] and arr[0][0].isdigit() and arr[1].isdigit() and len(arr[1]) <= 4:
                    # combination format like '2024/04/11,1350,...'
                    date_part = arr[0].strip()
                    time_part = arr[1].strip().zfill(4)  # ensure HHMM
                    hh = time_part[:2]
                    mm = time_part[2:]
                    # normalize date separators
                    if '/' in date_part:
                        dt_str = f"{date_part} {hh}:{mm}:00"
                        # try parsing with / separator
                        try:
                            dt = datetime.strptime(dt_str, "%Y/%m/%d %H:%M:%S")
                        except Exception:
                            dt = datetime.strptime(dt_str.replace('/', '-'), "%Y-%m-%d %H:%M:%S")
                    else:
                        dt_str = f"{date_part} {hh}:{mm}:00"
                        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    # replace first two tokens with single datetime, keep the rest
                    rest = arr[2:]
                    arr = [dt] + [float(x) for x in rest]
                else:
                    # original single-field datetime + numeric columns
                    arr = [float(arr[i]) if i > 0 else datetime.strptime(arr[0].strip(), "%Y-%m-%d %H:%M:%S") for i in
                           range(0, len(arr))]
            except Exception:
                # Fallback: try a couple of common datetime formats for the first token,
                # then coerce numeric values when possible.
                parsed = []
                first = arr[0].strip()
                dt = None
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"):
                    try:
                        dt = datetime.strptime(first, fmt)
                        break
                    except Exception:
                        continue
                if dt is not None:
                    parsed.append(dt)
                    for token in arr[1:]:
                        try:
                            parsed.append(float(token))
                        except Exception:
                            parsed.append(token)
                else:
                    # give up parsing dates; return tokens as-is with numeric coercion
                    for token in arr:
                        t = token.strip()
                        try:
                            parsed.append(float(t))
                        except Exception:
                            parsed.append(t)
                arr = parsed
        else:
            for i in range(len(arr)):
                if data_type[i] == "datetime":
                    arr[i] = datetime.strptime(arr[i], "%Y-%m-%d %H:%M:%S")
                elif data_type[i] == "float":
                    arr[i] = float(arr[i])
        self.extend(arr)

    def init_kline(self, kline):
        arr = [datetime.fromtimestamp(kline.time), kline.open, kline.high, kline.low, kline.close]
        self.extend(arr)
        return self

    def init_line(self, lines):
        arr = [lines[i] if i > 0 else datetime.strptime(lines[0], "%Y-%m-%d %H:%M:%S") for i in
               range(0, len(lines))]
        self.extend(arr)
        return self




BarList : List[DataItem] = {}
BarDict : Dict[datetime, DataItem] = {}


class ChartItemInfo:
    """
    图表数据信息
    """

    def __init__(self):
        self.type = ""
        self.discrete_list: BarList = []
        self.bars: BarDict = {}
        self.params: List[str] = []
        self.func_name: str = ""    # 获取数据的函数名
        self.data_type: List[str] = []
        self.max_height: int = 0
        self.symbol_code: str = ""
        self.symbol_name: str = ""
        self.symbol_period: str = ""


PlotIndex = NewType('PlotIndex', int)
ItemIndex = NewType('ItemIndex', int)
PlotItemInfo = Dict[ItemIndex, ChartItemInfo]
MinMaxIdxTuple = Tuple[int, int]
MinMaxPriceTuple = Tuple[float, float]


class Offset(Enum):
    """
    Offset of order/trade.
    """
    NONE = -1
    OPEN = 0
    CLOSE = 1
