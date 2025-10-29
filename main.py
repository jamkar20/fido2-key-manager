from PyQt5.QtWidgets import QApplication, QMessageBox
import sys
from dependencies.manager import Fido2Manager
from dependencies.ui.mainwindow import MainWindow


def main():
    app = QApplication(sys.argv)
    try:
        manager = Fido2Manager()
    except Exception:
        dlg = QMessageBox()
        dlg.setWindowTitle("Missing dependency")
        dlg.setText("python-fido2 is required. Install with: pip install python-fido2")
        dlg.setIcon(QMessageBox.Critical)
        dlg.exec_()
        sys.exit(1)

    win = MainWindow(manager)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
