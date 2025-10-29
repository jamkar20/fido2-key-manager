from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QMainWindow, QListWidget, QTextEdit, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QInputDialog
)


class MainWindow(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.setWindowTitle("FIDO2 Key Manager")
        self.resize(800, 600)

        self.device_list = QListWidget()
        self.refresh_btn = QPushButton("Refresh")
        self.info_view = QTextEdit()
        self.info_view.setReadOnly(True)
        self.set_pin_btn = QPushButton("Set PIN")
        self.change_pin_btn = QPushButton("Change PIN")
        self.reset_btn = QPushButton("Reset")
        self.exit_btn = QPushButton("Exit")

        left = QVBoxLayout()
        left.addWidget(QLabel("Connected Devices:"))
        left.addWidget(self.device_list)
        left.addWidget(self.refresh_btn)

        right = QVBoxLayout()
        right.addWidget(QLabel("Device Info:"))
        right.addWidget(self.info_view)

        pin_row = QHBoxLayout()
        pin_row.addWidget(self.set_pin_btn)
        pin_row.addWidget(self.change_pin_btn)
        right.addLayout(pin_row)

        bottom_row = QHBoxLayout()
        bottom_row.addWidget(self.reset_btn)
        bottom_row.addStretch()
        bottom_row.addWidget(self.exit_btn)
        right.addLayout(bottom_row)

        main_layout = QHBoxLayout()
        lw = QWidget()
        lw.setLayout(left)
        rw = QWidget()
        rw.setLayout(right)
        main_layout.addWidget(lw, 1)
        main_layout.addWidget(rw, 2)

        cw = QWidget()
        cw.setLayout(main_layout)
        self.setCentralWidget(cw)

        self.refresh_btn.clicked.connect(self.on_refresh)
        self.device_list.currentRowChanged.connect(self.on_select_device)
        self.set_pin_btn.clicked.connect(self.on_set_pin)
        self.change_pin_btn.clicked.connect(self.on_change_pin)
        self.reset_btn.clicked.connect(self.on_reset)
        self.exit_btn.clicked.connect(self.close)

        self.on_refresh()

    def show_error(self, title, msg):
        QMessageBox.critical(self, title, msg)

    def show_info(self, title, msg):
        QMessageBox.information(self, title, msg)

    def on_refresh(self):
        try:
            devices = self.manager.discover()
            self.device_list.clear()
            for d in devices:
                label = f"{d.get('product_string') or 'Unknown'}"
                self.device_list.addItem(label)
            self.info_view.setPlainText(f"Found {len(devices)} device(s)")
        except Exception as e:
            self.show_error("Discover failed", str(e))

    def on_select_device(self, idx: int):
        if idx < 0:
            return
        try:
            info = self.manager.select_device(idx)
            pretty = f"Path: {info['path']}\nVersions: {info['versions']}\nAAGUID: {info['aaguid']}\nExtensions: {info['extensions']}\nOptions: {info['options']}"
            self.info_view.setPlainText(pretty)
        except Exception as e:
            self.show_error("Select device failed", str(e))

    def on_set_pin(self):
        new_pin, ok = QInputDialog.getText(self, "Set PIN", "New PIN:")
        if not ok or not new_pin:
            return
        cur, ok2 = QInputDialog.getText(
            self, "Current PIN (optional)", "Current PIN:")
        if not ok2:
            return
        try:
            self.manager.set_pin(new_pin, cur or None)
            self.show_info("Success", "PIN set/changed successfully.")
        except Exception as e:
            self.show_error("Set PIN failed", str(e))

    def on_change_pin(self):
        cur, ok = QInputDialog.getText(self, "Change PIN", "Current PIN:")
        if not ok or not cur:
            return
        new_pin, ok2 = QInputDialog.getText(self, "Change PIN", "New PIN:")
        if not ok2 or not new_pin:
            return
        try:
            self.manager.change_pin(cur, new_pin)
            self.show_info("Success", "PIN changed successfully.")
        except Exception as e:
            self.show_error("Change PIN failed", str(e))

    def on_reset(self):
        confirm = QMessageBox.question(self, "Reset Authenticator", "This will factory-reset the authenticator. Continue?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return
        try:
            self.manager.reset()
            self.show_info("Success", "Authenticator reset (if supported)")
        except Exception as e:
            self.show_error("Reset failed", str(e))
