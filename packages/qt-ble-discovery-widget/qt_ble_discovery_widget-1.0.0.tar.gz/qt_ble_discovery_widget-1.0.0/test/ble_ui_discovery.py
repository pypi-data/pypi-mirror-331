from qt_ble_discovery_widget import QBLEDiscoveryWidget, BluetoothInfoFields, BluetoothDevice
from qtpy import QtWidgets
import asyncio
import sys
import PySide6.QtAsyncio as QtAsyncio

def print_changed_device(device: BluetoothDevice):
    print(f"Selected device: {device.name} ({device.address})")

async def start_scan(widget: QBLEDiscoveryWidget):
    """ Starts BLE scan asynchronously after UI is shown. """
    await widget.start_scan_with_discovery()

if __name__ == "__main__":
    
    app = QtWidgets.QApplication([])
    widget = QBLEDiscoveryWidget()
    widget.set_columns([field for field in BluetoothInfoFields])
    widget.selection_changed.connect(print_changed_device)
    widget.show()
    
    # Ensure async integration with Qt

    # Start stanning when the widget is shown

        # Start the scan **AFTER** the UI is shown
    from qtpy.QtCore import QTimer
    QTimer.singleShot(0, lambda: asyncio.create_task(start_scan(widget)))


    # with AsyncSlotRunner(debug=True):
    #     loop = asyncio.get_event_loop()
    #     loop.slow_callback_duration = 0.02

    #     loop.create_task(widget.start_scan_with_discovery())

    #     sys.exit(app.exec_())
    QtAsyncio.run(handle_sigint=True)
