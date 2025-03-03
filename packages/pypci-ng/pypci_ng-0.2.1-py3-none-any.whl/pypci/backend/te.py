import subprocess
import json
import re
import os
from pathlib import Path


COMMAND = 'Get-CimInstance -ClassName Win32_PnPEntity | Where-Object { $_.DeviceID -like "PCI*" } | Select-Object HardwareID | ConvertTo-JSON'
try:
    result = subprocess.run(["powershell", "-Command", COMMAND], capture_output=True, text=True)
except subprocess.SubprocessError:
    print("err")
    exit(-1)

hardware_ids = json.loads(result.stdout)


class PCI:
    def __init__(self):
        self.pci_data = {}
        self.pci_class = {}
        self.__LoadPciData()
        self.__LoadPciClass()

    def __LoadPciData(self):
        file_path = os.path.join(Path(__file__).parent, f"./pci.data.json")
        with open(file_path, "r") as f:
            self.pci_data = json.load(f)

    def __LoadPciClass(self):
        file_path = os.path.join(Path(__file__).parent, f"./pci.class.json")
        with open(file_path, "r") as f:
            self.pci_class = json.load(f)


pci = PCI()

for hardware_id in hardware_ids:
    device_ser = hardware_id["HardwareID"][0]
    class_ser = hardware_id["HardwareID"][-2]
    # device_ser = PCI\\VEN_8086&DEV_2F28&SUBSYS_00000000&REV_02
    pattern_device = r"VEN_([0-9A-Za-z]{4})&DEV_([0-9A-Za-z]{4})&SUBSYS_([0-9A-Za-z]{4})([0-9A-Za-z]{4})"
    match = re.search(pattern_device, device_ser)

    vendor_id = match.group(1).lower()
    device_id = match.group(2).lower()
    subsystem_vendor_id = match.group(4).lower()
    subsystem_device_id = match.group(3).lower()

    # vendor_id = device_ser[9:13]
    # device_id = device_ser[18:22]
    # subsystem_vendor_id = device_ser[34:38]
    # subsystem_device_id = device_ser[30:34]
    # class_ser = PCI\\VEN_8086&DEV_9D03&CC_010601
    pattern_class = r"CC_([0-9A-Fa-f]{6})"
    match = re.search(pattern_class, class_ser)
    class_id = match.group(1).lower()
    # class_id = class_ser[25:31]
    print(f"Vendor ID: {vendor_id} {pci.pci_data[vendor_id]['name']}")
    print(f"Device ID: {device_id} {pci.pci_data[vendor_id][device_id]['name']}")
    print(f"Subsystem Vendor ID: {subsystem_vendor_id}")
    print(f"Subsystem Device ID: {subsystem_device_id}")
    print(f"Class ID: {class_id}")
    print("__________")

