from functools import cached_property
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from typing import Dict
import time
from typing import Set
# from .data.mac_vendors import MAC_ADDR


class BluetoothDevice:
    device: BLEDevice
    last_advertisement_data: AdvertisementData | None = None

    num_updates: int = 1
    service_data: Dict[str, bytes]
    service_uuids: Set[str]
    manufacturer_data: Dict[int, bytes]
    last_advertisement_timestamp: float = 0

    def __init__(self, device: BLEDevice):
        super().__init__()

        self.device = device
        self.service_data = {}
        self.manufacturer_data = {}
        self.service_uuids = set()

    @property
    def full_name(self):
        return f"{self.name} ({self.address})"

    def record_advertising_data(
        self,
        device: BLEDevice,
        advertisement_data: AdvertisementData | None = None,
    ):
        assert self.device.address == device.address
        self.device = device
        self.last_advertisement_data = advertisement_data

        self.num_updates += 1

        if advertisement_data:
            self.service_data.update(advertisement_data.service_data)
            self.manufacturer_data.update(advertisement_data.manufacturer_data)
            self.service_uuids.update(advertisement_data.service_uuids)
            self.last_advertisement_timestamp = time.time()

    @property
    def address(self):
        return self.device.address

    @property
    def name(self):
        if not self.device.name:
            return "Unknown"
        
        return self.device.name

    @property
    def rssi(self):
        if self.last_advertisement_data:
            return self.last_advertisement_data.rssi
        return -100

    @property
    def age(self):
        return time.time() - self.last_advertisement_timestamp

    @property
    def device_uuid(self):
        return self.device.address

    @property
    def update_count(self):
        return self.num_updates

    # @cached_property
    # def vendor(self):
    #     # Sanitize the MAC address
    #     vendor_id: bytes = bytes.fromhex(self.address.replace(":", "")[:6])
    #     return MAC_ADDR.get(vendor_id, f"Unknown Vendor ({vendor_id.hex()})")
