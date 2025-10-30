from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
import sys
from dependencies.manager import Fido2Manager
from dependencies.ui.mainwindow import MainWindow
from dependencies.ui.theme import ThemeManager


def main():
    app = QApplication(sys.argv)
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    try:
        manager = Fido2Manager()
        theme = ThemeManager(app)
    except Exception:
        dlg = QMessageBox()
        dlg.setWindowTitle("Missing dependency")
        dlg.setText(
            "python-fido2 is required. Install with: pip install python-fido2")
        dlg.setIcon(QMessageBox.Critical)
        dlg.exec_()
        sys.exit(1)

    win = MainWindow(manager, theme)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    main()
