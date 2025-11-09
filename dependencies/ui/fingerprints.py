from PyQt5.QtWidgets import QVBoxLayout, QListWidget, QPushButton, QHBoxLayout,  QDialog, QMessageBox
from PyQt5.QtCore import Qt
from dependencies.ui.icon import LogoIcon
from ..manager import Fido2Manager
from .addfinger_window import AddFingerWindow


class FingerprintsWindow(QDialog):
    def __init__(self, manager: Fido2Manager, pin: str, parent=None, ):
        super().__init__(parent)
        self.pin = pin
        self.manager = manager
        self.__initWindow()

    def __initWindow(self):
        self.setWindowTitle("Fingerprints")
        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(LogoIcon())
        self.setFixedSize(400, 300)

        self.vLayout = QVBoxLayout()

        self.fingerprint_list = QListWidget()

        self.delete_btn = QPushButton("Delete")
        self.add_btn = QPushButton("Add")

        self.add_btn.clicked.connect(self._addFingerprint)
        self.delete_btn.clicked.connect(self._deleteFingerprint)

        self.vLayout.addWidget(self.fingerprint_list)

        hbox = QHBoxLayout()
        hbox.addWidget(self.delete_btn)
        hbox.addStretch()
        hbox.addWidget(self.add_btn)

        self.vLayout.addLayout(hbox)

        self.setLayout(self.vLayout)
        self._listFingerprints()

    def _listFingerprints(self):
        self.fingerprints = self.manager.list_fingerprints(self.pin)
        self.fingerprint_list.clear()
        self.fingerprint_list.itemClicked.connect(self._on_select_item)
        self.delete_btn.setEnabled(False)

        if not self.fingerprints:
            self.fingerprint_list.addItem("No fingerprints have been captured.")
            self.fingerprint_list.item(0).setFlags(Qt.NoItemFlags)  
            self.fingerprint_list.item(0).setForeground(Qt.gray)
        else:
            for v in self.fingerprints.values():
                self.fingerprint_list.addItem(v)

    def _on_select_item(self):
        self.delete_btn.setEnabled(True)

    def _addFingerprint(self):
        self.addfinger_window = AddFingerWindow(self.manager, self.pin, self)
        self.addfinger_window.exec_()
        self._listFingerprints()

    def show_error(self, title, msg):
        QMessageBox.critical(self, title, msg)

    def _deleteFingerprint(self):
        row = self.fingerprint_list.currentRow()
        if row < 0:
            self.show_error("No Fingerprint",
                            "Select a fingerprint to remove it")
            return

        reply = QMessageBox.question(
            self, "Delete Fingerprint", "Are you sure you want to delete fingerprint?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        key = list(self.fingerprints.keys())[
            self.fingerprint_list.currentRow()]

        self.manager.remove_fingerprint(self.pin, key)
        QMessageBox.information(
            self, "Success", "Fingerprint successfully deleted.")
        self._listFingerprints()
