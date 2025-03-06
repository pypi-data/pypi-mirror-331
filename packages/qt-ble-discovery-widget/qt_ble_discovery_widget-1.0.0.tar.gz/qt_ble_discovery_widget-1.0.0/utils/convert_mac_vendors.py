from typing import Dict

VENDOR_FILE = "mac-vendors.txt"

with open(VENDOR_FILE, "rb") as f:
    data = f.readlines()

MAC_ADDR: Dict[bytes,str] = {}

for line in data:
    split = line.decode().split(":")
    prefix, vendor = split[0], split[1]
    
    prefix_bytes: bytes = bytes.fromhex(prefix) 
    MAC_ADDR[prefix_bytes] = vendor
    
# Save to pytohn file as a dictionary
with open("src/ble_discovery_widget/data/mac_vendors.py", "w",encoding="utf-8") as f:
    f.write("MAC_ADDR = ")
    f.write(repr(MAC_ADDR))
    f.write("\n")