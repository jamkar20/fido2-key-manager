import sys
import os
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, QObject, QEvent
from PyQt5.QtWidgets import QApplication, QStyleFactory


class DarkTitleBarApplier(QObject):
    """Filter all windows titlebar darkmode"""

    def __init__(self, enable=True):
        super().__init__()
        self.enable = enable

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Show and hasattr(obj, "winId"):
            try:
                set_windows_dark_titlebar(obj, self.enable)
            except Exception:
                pass
        return super().eventFilter(obj, event)


class ThemeManager:
    def __init__(self, app: QApplication):
        self.app = app
        self.original_style_name = app.style().objectName()
        self.original_palette = QPalette(app.palette())

    def apply_dark(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        try:
            fusion = QStyleFactory.create("Fusion")
            if fusion is not None:
                self.app.setStyle(fusion)
        except Exception:
            pass

        self.app.setPalette(dark_palette)
        enable_dark_titlebar_globally(self.app, True)

    def restore_system(self):
        self.app.setPalette(QPalette(self.original_palette))
        enable_dark_titlebar_globally(self.app, False)
        try:
            if self.original_style_name:
                style = QStyleFactory.create(self.original_style_name)
                if style is not None:
                    self.app.setStyle(style)
                else:
                    self.app.setStyle(QStyleFactory.create("WindowsVista") or QStyleFactory.create(
                        "Windows") or QStyleFactory.create("Fusion"))
            else:
                self.app.setStyle(QStyleFactory.create("WindowsVista") or QStyleFactory.create(
                    "Windows") or QStyleFactory.create("Fusion"))
        except Exception:
            try:
                self.app.setStyle(QStyleFactory.create("Fusion"))
            except Exception:
                pass


def is_windows():
    return os.name == "nt" or sys.platform.startswith("win")


def set_windows_dark_titlebar(window, enable=True):
    if not is_windows():
        return
    try:
        import ctypes

        hwnd = int(window.winId())
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19
        set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
        value = ctypes.c_int(1 if enable else 0)

        res = set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                                   ctypes.byref(value), ctypes.sizeof(value))
        if res != 0:
            set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
                                 ctypes.byref(value), ctypes.sizeof(value))
    except Exception as e:
        pass


def enable_dark_titlebar_globally(app: QApplication, enable=True):
    if not is_windows():
        return

    for widget in app.topLevelWidgets():
        set_windows_dark_titlebar(widget, enable)

    filter_ = DarkTitleBarApplier(enable)
    app.installEventFilter(filter_)
    return filter_
