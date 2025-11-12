from PySide6 import QtCore, QtGui
from .chart_base import ChartBase
from .manager import BarManager


class ChartStraight(ChartBase):
    """
    直线图
    """

    def __init__(self, layout_index, chart_index, manager: BarManager):
        """"""
        super().__init__(layout_index, chart_index, manager)

    def _draw_item_picture(self, min_ix: int, max_ix: int) -> None:
        """
        Draw the picture of item in specific range.
        """
        if min_ix is None or max_ix is None:
            return

        self._item_picuture = QtGui.QPicture()
        painter = QtGui.QPainter(self._item_picuture)
        if not self._discrete_list:
            return
        for item in self._discrete_list:
            x1 = self.get_index(item[0])
            if x1 is None:
                print("********item[0]:{}".format(item[0]))
            y1 = item[1]
            x2 = self.get_index(item[2])
            if x2 is None:
                print("********item[2]:{}".format(item[2]))
            y2 = item[3]
            p = 0
            if x2 == x1:
                p = 0
            else:
                p = (y2 - y1) / (x2 - x1)

            if item[4] == 0:
                pass  # 线段
            elif item[4] == 2:  # 直线
                x1 = min_ix
                y1 = y2 - p * (x2 - x1)
                x2 = max_ix
                y2 = p * (x2 - x1) + y1
            elif item[4] == 1:  # 射线
                x2 = max_ix
                y2 = p * (x2 - x1) + y1
            # Choose base pen by color, and optionally override width if provided
            if len(item) > 5:
                base_pen = self.get_pen_by_color(item[5])
            else:
                base_pen = self._pens[-2]

            # If an explicit width is provided as 7th element, use it
            pen_to_use = base_pen
            if len(item) > 6:
                try:
                    width = float(item[6])
                    pen_to_use = QtGui.QPen(base_pen)
                    # set floating width for crisp scaling
                    try:
                        pen_to_use.setWidthF(width)
                    except Exception:
                        pen_to_use.setWidth(int(width))
                except Exception:
                    pass

            painter.setPen(pen_to_use)

            self._draw_bar_picture(painter, x1, y1, x2, y2)
            self._item_picuture.play(painter)
        painter.end()

    def _draw_bar_picture(self, painter, x1: int, y1: float, x2: int, y2: float):
        """"""
        # Create objects
        # line_picture = QtGui.QPicture()
        # painter = QtGui.QPainter(line_picture)

        # painter.setPen(self._pens[-2])
        painter.drawLine(
            QtCore.QPointF(x1, y1),
            QtCore.QPointF(x2, y2)
        )
        # Finish
        # painter.end()
        # return line_picture

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        text = ""
        return text
