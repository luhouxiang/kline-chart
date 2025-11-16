from PySide6 import QtWidgets, QtCore, QtGui


class KeyboardGenieWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.funcs = None
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setFixedWidth(260)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(4, 2, 4, 0)
        title_label = QtWidgets.QLabel("kline-chart 键盘精灵")
        title_label.setStyleSheet("font-weight: bold; color: #333333;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.close_button = QtWidgets.QPushButton("×")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                font-size: 18px;
                font-weight: bold;
                color: #555555;
            }
            QPushButton:hover {
                color: #d9534f;
            }
            """
        )
        self.close_button.setToolTip("关闭键盘精灵")
        self.close_button.clicked.connect(self._close_window)
        header_layout.addWidget(self.close_button)
        layout.addLayout(header_layout)

        content_frame = QtWidgets.QFrame()
        content_frame.setFrameShape(QtWidgets.QFrame.Panel)
        content_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        content_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid #b8b8b8;
                border-radius: 4px;
                background: #ffffff;
            }
            """
        )
        content_layout = QtWidgets.QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 4)
        content_layout.setSpacing(4)

        self.input_line_edit = QtWidgets.QLineEdit()
        self.input_line_edit.setPlaceholderText("请输入股票代码或名称")
        self.input_line_edit.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                padding: 5px;
                background: #f9f9fb;
            }
            """
        )
        content_layout.addWidget(self.input_line_edit)

        self.matching_list_widget = QtWidgets.QListWidget()
        self.matching_list_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.matching_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.matching_list_widget.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                background: #ffffff;
                padding: 2px;
            }
            QListWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QListWidget::item:selected:!active {
                background-color: #6CA9EE;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #DCEBFB;
            }
            """
        )
        content_layout.addWidget(self.matching_list_widget)
        layout.addWidget(content_frame)
        self.matching_list_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.matching_list_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        temp_item = QtWidgets.QListWidgetItem("示例文本")
        self.matching_list_widget.addItem(temp_item)
        item_height = self.matching_list_widget.sizeHintForRow(0)
        self.matching_list_widget.clear()

        visible_row_count = 12
        self.matching_list_widget.setFixedHeight(item_height * visible_row_count)

        self.setLayout(layout)
        self.hide()

        self.installEventFilter(self)
        self.input_line_edit.installEventFilter(self)
        app = QtWidgets.QApplication.instance()
        if app:
            app.installEventFilter(self)

        self.input_line_edit.textChanged.connect(self.on_input_text_changed)
        self.input_line_edit.returnPressed.connect(self.on_return_pressed)
        self.matching_list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self._close_window()
        elif key in (QtCore.Qt.Key_Up, QtCore.Qt.Key_Down):
            self.matching_list_widget.keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key == QtCore.Qt.Key_Escape:
                self._close_window()
                return True
            if obj is self.input_line_edit and key == QtCore.Qt.Key_Backspace:
                if not self.input_line_edit.text():
                    self._close_window()
                    return True
        elif event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonDblClick):
            if self.isVisible():
                local_pos = self.mapFromGlobal(event.globalPos())
                if not self.rect().contains(local_pos):
                    self._close_window()
                    return False
        return super().eventFilter(obj, event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._close_window()

    def on_input_text_changed(self, text):
        if self.parent():
            self.parent().update_matching_list(text)

    def on_return_pressed(self):
        selected_items = self.matching_list_widget.selectedItems()
        if selected_items:
            self._emit_selection(selected_items[0])
            return
        if self.matching_list_widget.count() > 0:
            item = self.matching_list_widget.item(0)
            self._emit_selection(item)
        else:
            print("没有匹配的股票代码")

    def on_item_double_clicked(self, item):
        self._emit_selection(item)

    def _emit_selection(self, item: QtWidgets.QListWidgetItem):
        if not item:
            return
        payload = item.data(QtCore.Qt.UserRole)
        print(f"选中股票候选：{payload}")
        if callable(self.funcs):
            self.funcs(payload)
        self.input_line_edit.clear()
        self._close_window()

    def _close_window(self):
        self.hide()
        parent = self.parent()
        if parent:
            parent.activateWindow()
            graph = getattr(parent, "graphWidget", None)
            if graph:
                graph.setFocus(QtCore.Qt.OtherFocusReason)
            else:
                parent.setFocus(QtCore.Qt.OtherFocusReason)
