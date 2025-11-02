# -*- coding: utf-8 -*-
import os
import sys
from PySide6 import QtWidgets
if "PyQt5" in sys.modules:
    del sys.modules["PyQt5"]

work_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print("work_dir: ", work_dir)
sys.path.append(work_dir)


def main():
    """Thin entrypoint: construct QApplication and show main window from gui module."""
    app = QtWidgets.QApplication(sys.argv)
    from klinechart.gui import MainWindow
    w = MainWindow()
    w.resize(1024, 768)
    w.show()
    app.exec()


if __name__ == '__main__':
    main()