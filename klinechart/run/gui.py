"""GUI module containing MainWindow. Keeps window/UI code separate from entrypoint."""
from pathlib import Path
from typing import Dict, List

from PySide6 import QtWidgets, QtCore, QtGui
from klinechart.chart import ChartWidget, ChartVolume, ChartCandle, ChartMacd, \
    ChartArrow, ChartLine, ChartStraight, ChartSignal, ItemIndex
from klinechart.chart.keyboard_genie_window import KeyboardGenieWindow
from klinechart.chart.object import PlotIndex, PlotItemInfo
from klinechart.run.config import conf
from .app_model import AppModel


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = AppModel(conf)
        self.model.load()
        datas: Dict[PlotIndex, PlotItemInfo] = self.model.get_datas()

        self.graphWidget = self._build_chart_widget(datas)
        self.setCentralWidget(self.graphWidget)

        self.keyboard_window = KeyboardGenieWindow(self)
        self.keyboard_window.funcs = self._handle_keyboard_selection
        self._symbol_candidates: List[Dict[str, str]] = []
        self._refresh_symbol_candidates()

    def _apply_algos_wrapper(self, klines, _datas):
        """Adapter so ChartWidget can ask the model to run algos."""
        self.model.apply_algos(klines)

    def _build_chart_widget(self, datas: Dict[PlotIndex, PlotItemInfo]) -> ChartWidget:
        """Create a fresh ChartWidget with plots/items wired up."""
        widget = ChartWidget(self)
        plots = conf["plots"]
        for plot_index, plot in enumerate(plots):
            axis = plot_index != len(plots) - 1
            widget.add_plot(
                hide_x_axis=axis,
                maximum_height=plots[plot_index]["max_height"]
            )
            for chart_item in plot["chart_item"]:
                if chart_item["type"] == "Candle":
                    widget.add_item(plot_index, ChartCandle)
                elif chart_item["type"] == "Volume":
                    widget.add_item(plot_index, ChartVolume)
                elif chart_item["type"] == "Line":
                    widget.add_item(plot_index, ChartLine)
                elif chart_item["type"] == "Macd":
                    widget.add_item(plot_index, ChartMacd)
                elif chart_item["type"] == "Arrow":
                    widget.add_item(plot_index, ChartArrow)
                elif chart_item["type"] == "Straight":
                    widget.add_item(plot_index, ChartStraight)
                elif chart_item["type"] == "Signal":
                    widget.add_item(plot_index, ChartSignal)
                else:
                    raise RuntimeError("not match item")

        widget.add_cursor()
        widget.update_all_history_data(datas, funcs=self._apply_algos_wrapper)
        return widget

    def handle_symbol_search_key(self, text: str) -> bool:
        """Show keyboard genie when the user types any alphabetical key."""
        normalized = (text or "").strip().upper()
        if not normalized or len(normalized) != 1 or not normalized.isalpha():
            return False
        self._refresh_symbol_candidates()
        if not self._symbol_candidates:
            return False
        self._show_keyboard_window(normalized)
        return True

    def _show_keyboard_window(self, initial_text: str) -> None:
        if not self.keyboard_window:
            return
        self.keyboard_window.input_line_edit.setText(initial_text)
        self.keyboard_window.adjustSize()
        self._position_keyboard_window()
        self.keyboard_window.show()
        self.keyboard_window.raise_()
        self.keyboard_window.activateWindow()
        self.keyboard_window.input_line_edit.setFocus()

    def _position_keyboard_window(self) -> None:
        """Place the floating window so its bottom-right corner matches the main window."""
        if not self.keyboard_window:
            return
        top_left = self.mapToGlobal(QtCore.QPoint(0, 0))
        size = self.keyboard_window.size()
        if size.width() == 0 or size.height() == 0:
            size = self.keyboard_window.sizeHint()
        bottom_right = top_left + QtCore.QPoint(self.width(), self.height())
        offset = 5
        x = bottom_right.x() - size.width() - offset
        y = bottom_right.y() - size.height() - offset
        min_x = top_left.x()
        min_y = top_left.y()
        max_x = bottom_right.x() - size.width()
        max_y = bottom_right.y() - size.height()
        x = min(max(x, min_x), max_x)
        y = min(max(y, min_y), max_y)
        self.keyboard_window.move(x, y)

    def _forward_key_to_keyboard_window(self, event: QtGui.QKeyEvent) -> bool:
        """Forward key events to the keyboard genie when it is visible."""
        keyboard = getattr(self, "keyboard_window", None)
        if not keyboard or not keyboard.isVisible():
            return False
        target = keyboard.input_line_edit
        if not target:
            return False
        clone = QtGui.QKeyEvent(
            event.type(),
            event.key(),
            event.modifiers(),
            event.text(),
            event.isAutoRepeat(),
            event.count()
        )
        QtWidgets.QApplication.sendEvent(target, clone)
        event.accept()
        return True

    def update_matching_list(self, text: str) -> None:
        """Update list widget with codes that match the current query."""
        if not self.keyboard_window:
            return
        normalized = (text or "").strip().upper()
        list_widget = self.keyboard_window.matching_list_widget
        list_widget.clear()
        query = normalized
        matches: List[Dict[str, str]] = []
        for candidate in self._symbol_candidates:
            code = candidate["code"]
            if not query or code.startswith(query):
                matches.append(candidate)
        for candidate in matches:
            item_text = f"{candidate['code']} | {candidate['filename']}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, candidate)
            list_widget.addItem(item)
        if matches:
            list_widget.setCurrentRow(0)

    def _handle_keyboard_selection(self, payload) -> None:
        """Callback from the keyboard genie with the chosen file."""
        if not payload:
            return
        if isinstance(payload, dict):
            file_path = payload.get("path", "")
        else:
            file_path = str(payload)
        if not file_path:
            return
        file_path = Path(file_path)
        if not file_path.exists():
            return
        self._set_primary_file_name(str(file_path))
        self._reload_chart_data()
        if self.graphWidget:
            self.graphWidget.setFocus()

    def _reload_chart_data(self) -> None:
        """Reload config data and refresh the chart widget."""
        if self.graphWidget:
            self.graphWidget.clear_all()
        self.model.load()
        datas = self.model.get_datas()
        if self.graphWidget:
            self.graphWidget.update_all_history_data(
                datas, funcs=self._apply_algos_wrapper
            )
        else:
            self.graphWidget = self._build_chart_widget(datas)
            self.setCentralWidget(self.graphWidget)
        self._refresh_symbol_candidates()

    def _refresh_symbol_candidates(self) -> None:
        """Scan the directory of the active file for possible stock codes."""
        base_file = self._get_primary_file_name()
        if not base_file:
            self._symbol_candidates = []
            return
        directory = Path(base_file).expanduser().parent
        if not directory.exists():
            self._symbol_candidates = []
            return
        candidates: List[Dict[str, str]] = []
        for file_path in sorted(directory.glob("*.txt")):
            code = self._extract_code_from_filename(file_path.name)
            if not code:
                continue
            candidates.append(
                {
                    "code": code,
                    "path": str(file_path),
                    "filename": file_path.name
                }
            )
        self._symbol_candidates = candidates

    def _get_primary_file_name(self) -> str:
        try:
            return str(self.model.conf["plots"][0]["chart_item"][0].get("file_name", ""))
        except (KeyError, IndexError, AttributeError):
            return ""

    def _set_primary_file_name(self, path: str) -> None:
        if not path:
            return
        try:
            self.model.conf["plots"][0]["chart_item"][0]["file_name"] = path
        except (KeyError, IndexError, AttributeError):
            pass

    @staticmethod
    def _extract_code_from_filename(filename: str) -> str:
        name = filename or ""
        if "#" not in name:
            return ""
        lower = name.lower()
        if not lower.endswith(".txt"):
            return ""
        start = name.index("#") + 1
        end = lower.rfind(".txt")
        if end <= start:
            return ""
        return name[start:end].upper()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """Ensure keyboard genie can be triggered whenever the window receives keys."""
        if self._forward_key_to_keyboard_window(event):
            return
        text = event.text()
        if text and self.handle_symbol_search_key(text):
            event.accept()
            return
        super().keyPressEvent(event)
