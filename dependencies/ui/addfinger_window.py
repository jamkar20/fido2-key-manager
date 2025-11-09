from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox, QInputDialog
from PyQt5.QtCore import QThread, pyqtSignal, QMetaObject, Qt, Q_ARG
from typing import Callable
from threading import Event
from ..manager import Fido2Manager
from .icon import LogoIcon, FingerprintWidget


class FingerprintWorker(QThread):
    touch_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    save_request_signal = pyqtSignal()
    save_name_signal = pyqtSignal(str)
    exit_event = Event()

    def __init__(self, manager: Fido2Manager, pin: str):
        super().__init__()
        self.exit_event.clear()
        self.manager = manager
        self.pin = pin
        self.fingerprint_name = "Fingerprint"
        self._save_callback_done = False
        self._save_name_received = None

    def run(self):
        try:
            self.manager.add_fingerprint(
                self.pin, self._on_touch_callback, self._on_save_callback, self.exit_event)
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))

    def _on_touch_callback(self, message: str):
        self.touch_signal.emit(message)

    def _on_save_callback(self):
        self._save_callback_done = False
        self._save_name_received = None
        self.save_request_signal.emit()

        while not self._save_callback_done:
            self.msleep(100)

        return self._save_name_received or "Fingerprint"

    def set_save_name(self, name: str):
        self._save_name_received = name
        self._save_callback_done = True


class AddFingerWindow(QDialog):
    def __init__(self, manager: Fido2Manager, pin: str, parent=None):
        super().__init__(parent)
        self.__initWindow()
        self.manager = manager
        self.pin = pin
        self.worker = None

    def __initWindow(self):
        self.setWindowTitle("Add Fingerprint")
        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowContextHelpButtonHint)
        self.setFixedSize(300, 300)
        self.setWindowIcon(LogoIcon())

        vbox = QVBoxLayout(self)

        self.fingerprint = FingerprintWidget()
        self.label = QLabel("")

        vbox.addWidget(self.fingerprint)
        vbox.addWidget(self.label)

    def showEvent(self, event):
        super().showEvent(event)
        self.start_fingerprint_operation()

    def start_fingerprint_operation(self):
        self.worker = FingerprintWorker(self.manager, self.pin)
        self.worker.touch_signal.connect(self.on_touch_message)
        self.worker.finished_signal.connect(self.on_operation_finished)
        self.worker.error_signal.connect(self.on_operation_error)
        self.worker.save_request_signal.connect(
            self.on_save_requested)
        self.worker.start()

    def on_touch_message(self, message: str):
        self.label.setText(message)

    def on_save_requested(self):
        name, ok = QInputDialog.getText(
            self,
            "Fingerprint Name",
            "Enter a name for this fingerprint:",
            text="Fingerprint"
        )

        if ok and name:
            self.worker.set_save_name(name)
        else:
            self.worker.set_save_name("Fingerprint")

    def on_operation_finished(self):
        QMessageBox.information(
            self, "Success", "Fingerprint added successfully!")
        self.close()

    def on_operation_error(self, error_message: str):
        self.label.setText(f"Error: {error_message}")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.exit_event.set()
            self.manager.cancel_enroll()
            self.worker.terminate()
            self.worker.wait()
        super().closeEvent(event)
