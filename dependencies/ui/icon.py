import sys
import os
from PyQt5.QtGui import QIcon



icon_path = ''

if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
    icon_path = os.path.join(base_path, "resources")
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_path, "./resources")

class LogoIcon(QIcon):
    def __init__(self):
        super().__init__(os.path.join(icon_path, "fido.png"))

