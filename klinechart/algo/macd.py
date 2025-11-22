from datetime import datetime
from typing import Dict, List

from klinechart.model.kline import KLine

from .formula import EMA


def calc_macd(
    klines: List[KLine],
    short_period: int = 12,
    long_period: int = 26,
    signal_period: int = 9,
) -> Dict[datetime, List[float]]:
    """Calculate MACD using EMA helpers so caller can render the series."""
    bars: Dict[datetime, List[float]] = {}
    if not klines:
        return bars

    short_ema = EMA(short_period)
    long_ema = EMA(long_period)
    signal_ema = EMA(signal_period)

    for k in klines:
        short_value = short_ema.input(k.close)
        long_value = long_ema.input(k.close)
        dif = short_value - long_value
        dea = signal_ema.input(dif)
        macd = 2 * (dif - dea)
        dt = datetime.fromtimestamp(k.time)
        bars[dt] = [dt, macd, dif, dea]

    return bars
