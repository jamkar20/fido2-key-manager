from PyQt5.QtWidgets import (
    QMainWindow, QListWidget, QTextEdit, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QInputDialog, QLineEdit, QAction, QMenu, QListWidgetItem
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from .icon import LogoIcon
from .theme import ThemeManager
import time


class DeviceDiscoverer(QThread):
    devices_found = pyqtSignal(list)

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self._running = True

    def run(self):
        while self._running:
            try:
                devices = self.manager.discover()
                self.devices_found.emit(devices)
            except:
                pass
            time.sleep(3)

    def stop(self):
        self._running = False
        self.quit()
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self, manager, theme: ThemeManager):
        super().__init__()
        self.manager = manager
        self.theme = theme
        self.setWindowTitle("FIDO2 Key Manager")
        self.setWindowIcon(LogoIcon())
        self.resize(800, 600)

        self.last_selected_path = None
        self.reset_pending = False
        self.reset_start_time = 0
        self.devices = []

        self.device_list = QListWidget()
        self.refresh_btn = QPushButton("Refresh")
        self.info_view = QTextEdit()
        self.info_view.setReadOnly(True)
        self.set_pin_btn = QPushButton("Set PIN")
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

        self.create_menubar()

        self.refresh_btn.clicked.connect(self.on_refresh)
        self.device_list.currentRowChanged.connect(self.on_select_device)
        self.device_list.itemClicked.connect(self.on_select_device)
        self.set_pin_btn.clicked.connect(self.on_set_pin)
        self.reset_btn.clicked.connect(self.on_reset)
        self.exit_btn.clicked.connect(self.on_exit)


        self.on_refresh()

    def create_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.on_exit)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("View")
        theme_menu = QMenu("Theme", self)

        dark_action = QAction("Dark", self)
        dark_action.triggered.connect(lambda: self.switch_theme(True))
        light_action = QAction("Light", self)
        light_action.triggered.connect(lambda: self.switch_theme(False))

        theme_menu.addAction(dark_action)
        theme_menu.addAction(light_action)
        view_menu.addMenu(theme_menu)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def switch_theme(self, dark: bool):
        if dark:
            self.theme.apply_dark()
        else:
            self.theme.restore_system()
        self.is_dark = dark

    def show_about(self):
        QMessageBox.information(
            self,
            "About FIDO2 Key Manager",
            "FIDO2 Key Manager\n\nDeveloped with ❤️ using PyQt5.\n\n© 2025 Jamal Kargar"
        )

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Exit", "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            event.ignore()

    def on_exit(self):
        self.close()

    def show_error(self, title, msg):
        QMessageBox.critical(self, title, msg)

    def show_info(self, title, msg):
        QMessageBox.information(self, title, msg)

    def update_device_list(self, devices):
        current_idx = self.device_list.currentRow()
        current_path = None
        if current_idx >= 0 and current_idx < len(self.devices):
            current_path = self.devices[current_idx].get('path')

        self.devices = devices
        self.device_list.blockSignals(True)
        self.device_list.clear()
        for d in devices:
            label = f"{d.get('product_string') or 'Unknown'}"
            self.device_list.addItem(label)
        self.device_list.blockSignals(False)

        if current_path:
            for i, d in enumerate(devices):
                if d.get('path') == current_path:
                    self.device_list.setCurrentRow(i)
                    break

        if not self.reset_pending:
            self.info_view.setPlainText(f"Found {len(devices)} device(s)")

    def on_refresh(self):
        try:
            devices = self.manager.discover()
            self.update_device_list(devices)
        except Exception as e:
            self.show_error("Discover failed", str(e))

    def on_select_device(self, idx: int | QListWidgetItem):
        try:
            if (isinstance(idx, QListWidgetItem)):
                idx = self.device_list.currentRow()

            if idx < 0 or idx >= len(self.devices):
                return
            device = self.devices[idx]
            self.last_selected_path = device.get('path')
            info = self.manager.select_device(idx)
            pretty = (
                f"Path: {info['path']}\n"
                f"Versions: {info['versions']}\n"
                f"AAGUID: {info['aaguid']}\n"
                f"Extensions: {info['extensions']}\n"
                f"Options: {info['options']}"
            )
            self.info_view.setPlainText(pretty)
            if self.manager.has_pin():
                self.set_pin_btn.setText("Change PIN")
            else:
                self.set_pin_btn.setText("Set PIN")
        except Exception as e:
            self.show_error("Select device failed", str(e))

    def on_set_pin(self):
        if self.device_list.currentRow() < 0:
            self.show_error("No Device", "Please select a device first.")
            return
        try:
            if self.manager.has_pin():
                self.on_change_pin()
            else:
                self.on_set_new_pin()
        except Exception as err:
            self.show_error("Error", str(err))

    def on_set_new_pin(self):
        new_pin, ok = QInputDialog.getText(
            self, "Set PIN", "New PIN:", QLineEdit.Password)
        if not ok or not new_pin:
            return
        confirm, ok2 = QInputDialog.getText(
            self, "Confirm PIN", "Confirm New PIN:", QLineEdit.Password)
        if not ok2 or confirm != new_pin:
            self.show_error("PIN Error", "PINs do not match.")
            return
        try:
            self.manager.set_pin(new_pin)
            self.show_info("Success", "PIN set successfully.")
            self.set_pin_btn.setText("Change PIN")
        except Exception as e:
            self.show_error("Set PIN failed", str(e))

    def on_change_pin(self):
        cur, ok = QInputDialog.getText(
            self, "Change PIN", "Current PIN:", QLineEdit.Password)
        if not ok or not cur:
            return
        new_pin, ok2 = QInputDialog.getText(
            self, "Change PIN", "New PIN:", QLineEdit.Password)
        if not ok2 or not new_pin:
            return
        confirm, ok3 = QInputDialog.getText(
            self, "Change PIN", "Confirm New PIN:", QLineEdit.Password)
        if not ok3 or confirm != new_pin:
            self.show_error("PIN Error", "New PINs do not match.")
            return
        try:
            self.manager.change_pin(cur, new_pin)
            self.show_info("Success", "PIN changed successfully.")
        except Exception as e:
            self.show_error("Change PIN failed", str(e))

    def on_reset(self):
        if self.device_list.currentRow() < 0:
            self.show_error("No Device", "Please select a device first.")
            return

        confirm = QMessageBox.question(
            self, "Reset Authenticator",
            "This will factory-reset the authenticator.\n"
            "You must disconnect and reconnect the device within 10 seconds.\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        self.reset_pending = True
        self.reset_start_time = time.time()
        self.info_view.setPlainText(
            "Please DISCONNECT the device now and RECONNECT it within 10 seconds..."
        )

        self.setEnabled(False)

        QTimer.singleShot(1000, self.check_disconnect_for_reset)

    def check_disconnect_for_reset(self):
        if not self.reset_pending:
            return

        try:
            elapsed = time.time() - self.reset_start_time
            if elapsed > 10:
                self.reset_pending = False
                self.show_error(
                    "Reset Timeout", "Device was not disconnected within 10 seconds.")
                self.on_refresh()
                self.setEnabled(True)
                return
            current_devices = self.manager.discover()
            if any(dev.get('path') == self.last_selected_path for dev in current_devices):
                self.info_view.setPlainText(
                    "Waiting for device to be disconnected...")
                QTimer.singleShot(1000, self.check_disconnect_for_reset)
                return
            else:
                self.waiting_for_disconnect = False
                self.info_view.setPlainText(
                    "Device disconnected. Please RECONNECT within 10 seconds...")
                self.reset_start_time = time.time()  # شروع شمارش دوباره برای reconnect
                QTimer.singleShot(1000, self.check_reconnect_for_reset)
        except Exception as e:
            self.info_view.setPlainText(
                f"Error while checking disconnect: {str(e)}")
            QTimer.singleShot(1000, self.check_disconnect_for_reset)

    def check_reconnect_for_reset(self):
        if not self.reset_pending or self.waiting_for_disconnect:
            self.setEnabled(True)
            return

        elapsed = time.time() - self.reset_start_time
        if elapsed > 10:
            self.reset_pending = False
            self.show_error("Reset Timeout",
                            "Device was not reconnected within 10 seconds.")
            self.on_refresh()
            self.setEnabled(True)
            return

        try:
            current_devices = self.manager.discover()
            if len(current_devices) == 0:
                remaining = int(10 - elapsed)
                self.info_view.setPlainText(
                    f"Waiting for reconnection... ({remaining}s left)")
                QTimer.singleShot(1000, self.check_reconnect_for_reset)
                return

            reconnected = None
            for dev in current_devices:
                if dev.get('path') == self.last_selected_path:
                    reconnected = dev
                    break

            if not reconnected:
                remaining = int(10 - elapsed)
                self.info_view.setPlainText(
                    f"Wrong device reconnected. Waiting for correct one... ({remaining}s left)"
                )
                QTimer.singleShot(1000, self.check_reconnect_for_reset)
                return

            self.reset_pending = False
            self.manager.select_device(self.devices.index(reconnected))
            self.manager.reset()
            self.show_info("Success", "Authenticator reset successfully!")
            self.on_refresh()
            self.setEnabled(True)

        except Exception as e:
            remaining = int(10 - elapsed)
            self.info_view.setPlainText(
                f"Error during reset check: {str(e)}\nRetrying... ({remaining}s left)"
            )
            QTimer.singleShot(1000, self.check_reconnect_for_reset)
