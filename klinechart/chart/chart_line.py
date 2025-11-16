from typing import Optional, Tuple, List

from PySide6 import QtCore, QtGui
from klinechart.chart.object import DataItem
from .chart_base import ChartBase
from .manager import BarManager


class ChartLine(ChartBase):
    """
    曲线图
    """

    def __init__(self, layout_index, chart_index, manager: BarManager):
        """"""
        super().__init__(layout_index, chart_index, manager)
        self._custom_line_pens: List[Optional[QtGui.QPen]] = []

    def _draw_bar_picture(self, ix: int, old_bar: DataItem, bar: DataItem) -> QtGui.QPicture:
        """"""
        # Create objects
        line_picture = QtGui.QPicture()
        painter = QtGui.QPainter(line_picture)
        if bar:
            for i in range(1, len(bar)):
                pen = self._get_line_pen(i - 1)
                painter.setPen(pen)
                if old_bar[i] == 0 and bar[i] == 0:
                    continue
                painter.drawLine(
                    QtCore.QPointF(ix - 1, old_bar[i]),
                    QtCore.QPointF(ix, bar[i])
                )

        # Finish
        painter.end()
        return line_picture

    def update_history_data(self, info):
        super().update_history_data(info)
        cleaned_params = []
        custom_pens: List[Optional[QtGui.QPen]] = []
        for entry in self._params:
            label, color_name = self._parse_param_entry(entry)
            cleaned_params.append(label)
            pen = self._create_custom_pen(color_name) if color_name else None
            custom_pens.append(pen)
        self._params = cleaned_params
        self._custom_line_pens = custom_pens

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        bar = self.get_bar_from_index(ix)

        if bar:
            text = ""
            for i in range(1, len(bar) - 1):
                if len(self._params) >= i:
                    text += "{}:".format(self._params[i - 1])
                text += "{:.2f}, ".format(bar[i])  # f"{(bar[i])}, "
                if i % 2 == 0:
                    text += "\n"
            if len(self._params) >= len(bar) - 1:
                text += "{}:".format(self._params[len(bar) - 1 - 1])
            text += "{:.3f}".format(bar[-1])  # f"{(bar[-1])}"
        else:
            text = ""

        return text

    def _get_line_pen(self, index: int) -> QtGui.QPen:
        if 0 <= index < len(self._custom_line_pens) and self._custom_line_pens[index]:
            return self._custom_line_pens[index]
        if index < len(self._pens):
            return self._pens[index]
        return self._up_pen

    def _create_custom_pen(self, color_name: Optional[str]) -> Optional[QtGui.QPen]:
        if not color_name:
            return None
        color = QtGui.QColor(color_name)
        if not color.isValid():
            return None
        return self._make_pen(color)

    @staticmethod
    def _parse_param_entry(entry) -> Tuple[str, Optional[str]]:
        label = ""
        color_name = None
        if isinstance(entry, str):
            parts = entry.split(":", 1)
            label = parts[0].strip()
            if len(parts) > 1:
                color_candidate = parts[1].strip()
                color_name = color_candidate if color_candidate else None
        elif isinstance(entry, dict):
            label = str(entry.get("name", "")).strip()
            color_candidate = entry.get("color")
            if isinstance(color_candidate, str) and color_candidate.strip():
                color_name = color_candidate.strip()
        else:
            label = str(entry)
        if not label:
            label = ""
        return label, color_name

