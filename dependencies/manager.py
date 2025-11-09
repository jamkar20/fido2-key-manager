from typing import List, Optional, Dict, Any, Callable
from fido2.hid import CtapHidDevice
from fido2.ctap2 import ClientPin
from fido2.ctap2.base import Ctap2
from fido2.ctap2.bio import BioEnrollment, FPBioEnrollment, CaptureError


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
            ctap.reset(event=None)
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

    def support_bio(self) -> bool:
        """Check if the selected key support Biometric."""
        _, ctap = self.selected
        info = ctap.get_info()
        return BioEnrollment.is_supported(info)

    def can_add_fingerprint(self) -> bool:
        if not self.support_bio():
            raise RuntimeError('Device is not support biometric!')
        _, ctap = self.selected
        info = ctap.get_info()
        if not info.options.get("clientPin"):
            raise RuntimeError("PIN not set for the device!")
        return True

    def _get_bio(self, pin: str):
        _, ctap = self.selected
        client_pin = ClientPin(ctap)
        pin_token = client_pin.get_pin_token(
            pin, ClientPin.PERMISSION.BIO_ENROLL)
        return FPBioEnrollment(ctap, client_pin.protocol, pin_token)

    def cancel_enroll(self):
        if self.enroller:
            self.enroller.cancel()

    def add_fingerprint(self, pin: str, on_touch: Optional[Callable[[str], Any]], on_save: Optional[Callable[[], str]], event=None):
        if not callable(on_touch):
            def _on_touch(s: str):
                return
            on_touch = _on_touch

        bio = self._get_bio(pin)
        self.enroller = bio.enroll()

        template_id = None
        on_touch("Press your fingerprint against the sensor now...")
        while template_id is None:
            try:
                template_id = self.enroller.capture(event)
                if self.enroller.remaining > 0:
                    on_touch(str(self.enroller.remaining) +
                             " more scans needed. touch sensor now ...")
            except CaptureError as e:
                raise e
        self.enroller = None
        f_name = "Fingerprint"
        if callable(on_save):
            f_name = on_save()
        bio.set_name(template_id, f_name)

    def list_fingerprints(self, pin: str):
        bio = self._get_bio(pin)
        return bio.enumerate_enrollments()

    def remove_fingerprint(self, pin: str, template_id: bytes):
        bio = self._get_bio(pin)
        bio.remove_enrollment(template_id)

    def rename_fingerprint(self, pin: str, template_id: bytes, new_name: str):
        bio = self._get_bio(pin)
        bio.set_name(template_id, new_name)
