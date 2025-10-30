from typing import List, Optional, Dict, Any
from fido2.hid import CtapHidDevice
from fido2.ctap2 import ClientPin
from fido2.ctap2.base import Ctap2


class DeviceNotSelectedError(Exception):
    pass


class Fido2Manager:
    def __init__(self):
        self.devices = []
        self.selected = None

    def discover(self) -> List[Dict[str, Any]]:
        found = []
        self.devices = list(CtapHidDevice.list_devices())
        for dev in self.devices:
            found.append({
                "path": dev.descriptor.path,
                "vendor_id": getattr(dev.descriptor, "vid", None),
                "product_id": getattr(dev.descriptor, "pid", None),
                "product_string": getattr(dev.descriptor, "product_name", None),
            })
        return found

    def select_device(self, index: int):
        if not self.devices:
            raise RuntimeError("No devices discovered")
        dev = self.devices[index]
        ctap = Ctap2(dev)
        self.selected = (dev, ctap)
        return self.get_info()

    def get_info(self) -> Dict[str, Any]:
        if not self.selected:
            raise DeviceNotSelectedError()
        dev, ctap = self.selected
        info = ctap.get_info()
        return {
            "path": dev.descriptor.path,
            "versions": info.versions,
            "aaguid": getattr(info, "aaguid", b"").hex(),
            "extensions": list(getattr(info, "extensions", [])),
            "options": getattr(info, "options", {}),
        }

    def set_pin(self, new_pin: str, current_pin: Optional[str] = None) -> bool:
        pin = ClientPin(self.selected[1])
        if current_pin:
            pin.change_pin(current_pin, new_pin)
        else:
            pin.set_pin(new_pin)
        return True

    def change_pin(self, current_pin: str, new_pin: str) -> bool:
        return self.set_pin(new_pin, current_pin)

    def reset(self) -> bool:
        _, ctap = self.selected
        if hasattr(ctap, "reset"):
            ctap.reset(event=None, on_keepalive=on_keepalive)
            return True
        raise RuntimeError("Reset not supported")

    def has_pin(self) -> bool:
        """Check if the selected key has a PIN set."""
        if not self.selected:
            raise DeviceNotSelectedError()

        _, ctap = self.selected
        info = ctap.get_info()
        options = getattr(info, "options", {})
        return options.get("clientPin", False)
