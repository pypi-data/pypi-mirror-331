import logging
from typing import Dict, List

import bleak
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from qt_custom_treewidget import ColumnNames, TreeItem, TreeviewViewer
from qtpy import QtCore, QtWidgets, QtGui
from .objects import BluetoothDevice
import re

class BluetoothInfoFields(ColumnNames):
    NAME = "Name"
    ADDRESS = "Address"
    RSSI = "RSSI"
    SERVICE_UUIDS = "Service UUIDs"
    SERVICE_DATA = "Service Data"
    MANUFACTURER_DATA = "Manufacturer Data"
    DEVICE_UUID = "Device UUID"
    UPDATE_COUNT = "Update Count"
    AGE = "Age"
    MERGED_DEVICE_INFO = "Device"
    # VENDOR = "Vendor"


class BluetoothTreeItem(TreeItem):
    fade_age_threshold: float | None = None

    def __init__(self, device: BluetoothDevice, fade_age_threshold: float | None):
        super().__init__()
        self.device = device
        self.fade_age_threshold = fade_age_threshold

    def get_text(self, column_type: ColumnNames) -> str:
        if column_type == BluetoothInfoFields.NAME:
            return self.device.name if self.device.name else "Unknown"
        elif column_type == BluetoothInfoFields.ADDRESS:
            return self.device.address
        elif column_type == BluetoothInfoFields.RSSI:
            return str(self.device.rssi)
        elif column_type == BluetoothInfoFields.SERVICE_DATA:
            return str(self.device.service_data)
        elif column_type == BluetoothInfoFields.MANUFACTURER_DATA:
            return str(self.device.manufacturer_data)
        elif column_type == BluetoothInfoFields.SERVICE_UUIDS:
            return str(self.device.service_uuids)
        elif column_type == BluetoothInfoFields.DEVICE_UUID:
            return str(self.device.device_uuid)
        elif column_type == BluetoothInfoFields.UPDATE_COUNT:
            return str(self.device.update_count)
        elif column_type == BluetoothInfoFields.AGE:
            return f"{self.device.age:.1f}s"
        elif column_type == BluetoothInfoFields.MERGED_DEVICE_INFO:
            return f"{self.device.name} ({self.device.address})"
        # elif column_type == BluetoothInfoFields.VENDOR:
            # return self.device.vendor
        return "Unknown"

    def apply_filter(self, regex: re.Pattern | None | str):
        if isinstance(regex, str):
            regex = re.compile(regex, re.IGNORECASE)

        if regex is None:
            self.setHidden(False)
            return

        match = regex.search(self.device.name) or regex.search(self.device.address)
        self.setHidden(not match)

    def get_color(self) -> QtGui.QColor | None:
        if self.fade_age_threshold is None:
            return None

        if self.device.age > self.fade_age_threshold * 2:
            return QtGui.QColor(0, 0, 0, 100)

        elif self.device.age > self.fade_age_threshold:
            return QtGui.QColor(0, 0, 0, 50)

    @property
    def is_stale(self) -> bool:
        if self.fade_age_threshold is None:
            return False

        return self.device.age > self.fade_age_threshold

    @property
    def is_very_stale(self) -> bool:
        if self.fade_age_threshold is None:
            return False
        return self.device.age > self.fade_age_threshold * 2

    def __lt__(self, other: "BluetoothTreeItem") -> bool:  # type: ignore

        if self.is_very_stale and not other.is_very_stale:
            return True
        elif not self.is_very_stale and other.is_very_stale:
            return False
        
        column = self.treeWidget().itemDelegateForColumn(self.treeWidget().sortColumn()).collumn_type  # type: ignore

        if column == BluetoothInfoFields.AGE:
            return self.device.age < other.device.age
        elif column == BluetoothInfoFields.RSSI:
            return self.device.rssi < other.device.rssi
        else:
            return str(self.get_text(column)) < str(other.get_text(column))


class QBLEDiscoveryWidget(QtWidgets.QWidget):
    selection_changed = QtCore.Signal(BluetoothDevice)
    devices: Dict[str, "BluetoothDevice"]
    treeitems: Dict[BluetoothDevice, BluetoothTreeItem]
    regex: str | None = None

    FADE_AGE_THRESHOLD = 30

    def __init__(self, parent=None, auto_update: bool = True):
        super().__init__(parent)

        self.devices = {}
        self.treeitems = {}

        self.viewer_widget = TreeviewViewer()
        self.viewer_widget.itemSelectionChanged.connect(self.on_selection_change)
        self.log = logging.getLogger(__name__)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.viewer_widget)

        self.setLayout(layout)

        if auto_update:
            self.update_timer = QtCore.QTimer()
            self.update_timer.setInterval(500)
            self.update_timer.timeout.connect(self.viewer_widget.refresh_ui)
            self.update_timer.start()

        # Allow sorting
        self.viewer_widget.setSortingEnabled(True)

    def on_selection_change(self):
        selected_items = self.viewer_widget.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]

        if isinstance(item, BluetoothTreeItem):
            self.selection_changed.emit(item.device)

    def set_columns(self, collumns: List[ColumnNames]):
        self.viewer_widget.set_columns(collumns)

    async def start_scan_with_discovery(self):
        self.ble_scanner = bleak.BleakScanner(detection_callback=self.scan_data_callback, scanning_mode="active")
        await self.ble_scanner.start()

    async def scan_data_callback(
        self,
        device: BLEDevice,
        advertisement_data: AdvertisementData | None = None,
    ):
        address: str = device.address

        if address not in self.devices:
            self.log.debug(f"Discovered new device: {device.name} ({device.address})")
            self.devices[address] = BluetoothDevice(device)

        self.devices[address].record_advertising_data(device, advertisement_data)

        if self.devices[address] not in self.treeitems:
            item = BluetoothTreeItem(self.devices[address], fade_age_threshold=self.FADE_AGE_THRESHOLD)
            self.viewer_widget.add(item)
            item.apply_filter(self.regex)
            self.treeitems[self.devices[address]] = item

        # Update sorting
        self.viewer_widget.sortItems(self.viewer_widget.sortColumn(), self.viewer_widget.header().sortIndicatorOrder())

    @property
    def selected_device(self) -> BluetoothDevice | None:
        selected_items = self.viewer_widget.get_selected_items()
        if not selected_items:
            return None
        assert len(selected_items) == 1
        assert isinstance(selected_items[0], BluetoothTreeItem)
        return selected_items[0].device

    def set_filter(self, regex: str | None):
        self.regex = regex

        # Compile the regex pattern
        if self.regex is None:
            pattern = None
        else:
            pattern = re.compile(self.regex, re.IGNORECASE)

        # Iterate through all devices and update visibility based on regex matching
        for tree_item in self.treeitems.values():
            tree_item.apply_filter(pattern)
