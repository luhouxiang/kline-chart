"""Application model: encapsulates data and algorithm operations.

UI should interact with this model rather than directly loading files or calling algos.
"""
from typing import Dict
from klinechart.chart.object import PlotIndex, PlotItemInfo
from klinechart.run.config import conf
from .data_loader import load_data
from .algos import obtain_data_from_algo


class AppModel:
    """Model holding chart data and exposing algorithm application APIs."""

    def __init__(self, conf_dict: Dict = None):
        self.conf = conf_dict or conf
        self._datas: Dict[PlotIndex, PlotItemInfo] = {}

    def load(self):
        """Load data according to config into internal storage."""
        self._datas = load_data(self.conf)

    def get_datas(self) -> Dict[PlotIndex, PlotItemInfo]:
        """Return loaded datas; call load() first."""
        return self._datas

    def get_initial_bars(self):
        """Return bars for the first plot/item (used to seed a manager)."""
        if not self._datas:
            return None
        return self._datas[PlotIndex(0)][0].bars.values()

    def apply_algos(self, klines: list):
        """Apply algorithm callbacks to populate datas using provided klines."""
        if not self._datas:
            # nothing loaded
            return
        obtain_data_from_algo(klines, self._datas)
