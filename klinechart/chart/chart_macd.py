from PySide6 import QtCore, QtGui
from klinechart.chart.object import DataItem
from .chart_base import ChartBase
from .base import BAR_WIDTH
from .manager import BarManager


class ChartMacd(ChartBase):
    """ macd图
    """

    def __init__(self, layout_index, chart_index, manager: BarManager):
        """"""
        super().__init__(layout_index, chart_index, manager)

    def _draw_bar_picture(self, ix: int, old_bar: DataItem, bar: DataItem) -> QtGui.QPicture:
        """"""
        # Create objects
        volume_picture = QtGui.QPicture()
        painter = QtGui.QPainter(volume_picture)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        # Set painter color
        if bar[1] >= 0:
            painter.setPen(self._up_pen)
            painter.setBrush(self._up_brush)
        else:
            painter.setPen(self._down_pen)
            painter.setBrush(self._down_brush)

        # Draw volume body
        rect = QtCore.QRectF(
            ix - BAR_WIDTH,
            0,
            BAR_WIDTH * 2,
            bar[1]
        )
        painter.drawRect(rect)

        prev_bar = old_bar if old_bar else bar
        painter.setPen(self._magenta_pen)
        dif_line = QtCore.QLineF(ix - 1, prev_bar[2], ix, bar[2])
        painter.drawLine(dif_line)

        painter.setPen(self._yellow_pen)
        dea_line = QtCore.QLineF(ix - 1, prev_bar[3], ix, bar[3])
        painter.drawLine(dea_line)

        # Finish
        painter.end()
        return volume_picture

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        bar = self.get_bar_from_index(ix)

        if bar:
            text = f"macd:{bar[1]},dif:{bar[2]},dea:{bar[3]}"
        else:
            text = ""

        return text

