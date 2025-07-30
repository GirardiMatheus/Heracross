import subprocess
import re
import os
import json

def get_usb_info(include_details=False):
    """Get comprehensive USB information including devices and controller details"""
    devices_info = get_usb_devices_info(include_details)
    
    result = {
        "Devices": devices_info
    }
    
    # Only include controllers in detailed mode
    if include_details:
        controllers_info = get_usb_controllers_info()
        result["Controllers"] = controllers_info
    
    return result

def get_usb_devices_info(include_details=False):
    """Get USB devices information using lsusb and additional sources"""
    try:
        if include_details:
            result = subprocess.run(
                ["lsusb", "-v"],
                capture_output=True, text=True, check=True,
                env={**os.environ, "LC_ALL": "C"}
            )
            return parse_lsusb_verbose_output(result.stdout)
        else:
            result = subprocess.run(
                ["lsusb"],
                capture_output=True, text=True, check=True,
                env={**os.environ, "LC_ALL": "C"}
            )
            return parse_lsusb_basic_output(result.stdout, summary=True)
            
    except subprocess.CalledProcessError:
        return get_usb_devices_fallback(include_details)
    except FileNotFoundError:
        return get_usb_devices_fallback(include_details)
    except Exception as e:
        return [{"Error": f"Could not get USB devices info: {str(e)}"}]

def parse_lsusb_basic_output(output, summary=False):
    """Parse basic lsusb output"""
    devices = []
    
    for line in output.strip().splitlines():
        if line.strip():
            # Parse line format: Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
            match = re.match(r'Bus (\d+) Device (\d+): ID ([0-9a-f]{4}):([0-9a-f]{4})\s+(.+)', line)
            if match:
                bus, device, vendor_id, product_id, description = match.groups()
                
                if summary:
                    # Skip root hubs and show only user devices in summary mode
                    if "root hub" in description.lower():
                        continue
                    
                    # Simplified output for summary
                    device_info = {
                        "Device": clean_device_name(description),
                        "Type": get_device_type(description, vendor_id, product_id),
                        "Bus": f"USB {get_usb_version(description)}"
                    }
                else:
                    # Full output for detailed mode
                    device_info = {
                        "Bus": bus,
                        "Device": device,
                        "Vendor ID": vendor_id,
                        "Product ID": product_id,
                        "Description": description.strip()
                    }
                    
                    # Try to get vendor and product names
                    vendor_product = description.strip().split(' ', 1)
                    if len(vendor_product) >= 2:
                        device_info["Vendor"] = vendor_product[0]
                        device_info["Product"] = vendor_product[1]
                
                devices.append(device_info)
    
    return devices if devices else [{"Status": "No user USB devices found"}]

def clean_device_name(description):
    """Clean and simplify device name for user-friendly display"""
    # Remove company suffixes and technical terms
    cleaned = description
    
    # Remove common company suffixes
    suffixes_to_remove = [
        ", Inc.", " Inc.", " Corp.", " Corporation", " Co., Ltd", " Technology", 
        " Technologies", " Ltd.", " Limited", " S.A.", " GmbH", " AG"
    ]
    
    for suffix in suffixes_to_remove:
        cleaned = cleaned.replace(suffix, "")
    
    # Simplify common device names
    simplifications = {
        "USB Audio Device": "Audio Device",
        "Wireless Receiver": "Wireless Device",
        "Universal Receiver": "Wireless Receiver",
        "USB Receiver": "Wireless Receiver"
    }
    
    for old, new in simplifications.items():
        if old in cleaned:
            cleaned = new
            break
    
    # Remove redundant words
    words_to_remove = ["USB", "Device"]
    words = cleaned.split()
    filtered_words = []
    
    for word in words:
        if word not in words_to_remove or len(filtered_words) == 0:
            filtered_words.append(word)
    
    return " ".join(filtered_words)

def get_device_type(description, vendor_id, product_id):
    """Determine device type based on description and IDs"""
    desc_lower = description.lower()
    
    # Audio devices
    if any(keyword in desc_lower for keyword in ["audio", "sound", "speaker", "headset", "microphone"]):
        return "Audio"
    
    # Input devices
    if any(keyword in desc_lower for keyword in ["mouse", "keyboard", "trackpad", "touchpad"]):
        return "Input"
    
    # Wireless receivers
    if any(keyword in desc_lower for keyword in ["receiver", "wireless", "bluetooth"]):
        return "Wireless"
    
    # Storage devices
    if any(keyword in desc_lower for keyword in ["storage", "disk", "drive", "flash"]):
        return "Storage"
    
    # Cameras
    if any(keyword in desc_lower for keyword in ["camera", "webcam", "video"]):
        return "Camera"
    
    # Printers
    if any(keyword in desc_lower for keyword in ["printer", "scanner"]):
        return "Printer"
    
    # Network devices
    if any(keyword in desc_lower for keyword in ["ethernet", "wifi", "network", "lan"]):
        return "Network"
    
    # Mobile devices
    if any(keyword in desc_lower for keyword in ["phone", "android", "iphone", "mobile"]):
        return "Mobile"
    
    # Default
    return "Device"

def get_usb_version(description):
    """Determine USB version from description"""
    desc_lower = description.lower()
    
    if "3." in desc_lower or "usb3" in desc_lower:
        return "3.0+"
    elif "2." in desc_lower or "usb2" in desc_lower:
        return "2.0"
    elif "1." in desc_lower or "usb1" in desc_lower:
        return "1.1"
    else:
        return "2.0"  

def parse_lsusb_verbose_output(output):
    """Parse verbose lsusb output for detailed information"""
    devices = []
    current_device = {}
    in_device_section = False
    
    for line in output.splitlines():
        line = line.strip()
        
        # Start of new device
        if line.startswith("Bus") and "Device" in line and "ID" in line:
            if current_device:
                devices.append(current_device)
            
            # Parse device header
            match = re.match(r'Bus (\d+) Device (\d+): ID ([0-9a-f]{4}):([0-9a-f]{4})\s+(.+)', line)
            if match:
                bus, device, vendor_id, product_id, description = match.groups()
                current_device = {
                    "Bus": bus,
                    "Device": device,
                    "Vendor ID": vendor_id,
                    "Product ID": product_id,
                    "Description": description.strip()
                }
                in_device_section = True
        
        elif in_device_section and line:
            # Parse device descriptor fields
            if line.startswith("bcdUSB"):
                current_device["USB Version"] = line.split()[-1]
            elif line.startswith("bDeviceClass"):
                class_info = line.split(None, 1)[1] if len(line.split(None, 1)) > 1 else ""
                current_device["Device Class"] = class_info
            elif line.startswith("bMaxPacketSize0"):
                current_device["Max Packet Size"] = line.split()[-1]
            elif line.startswith("bcdDevice"):
                current_device["Device Version"] = line.split()[-1]
            elif line.startswith("iManufacturer") and len(line.split()) > 3:
                manufacturer = " ".join(line.split()[3:])
                current_device["Manufacturer"] = manufacturer
            elif line.startswith("iProduct") and len(line.split()) > 3:
                product = " ".join(line.split()[3:])
                current_device["Product Name"] = product
            elif line.startswith("iSerial") and len(line.split()) > 3:
                serial = " ".join(line.split()[3:])
                current_device["Serial Number"] = serial
            elif line.startswith("bNumConfigurations"):
                current_device["Configurations"] = line.split()[-1]
        
        elif line.startswith("Bus") or not line:
            in_device_section = False
    
    # Add the last device
    if current_device:
        devices.append(current_device)
    
    return devices if devices else [{"Warning": "No USB devices found"}]

def get_usb_devices_fallback(include_details=False):
    """Fallback method to get USB devices without lsusb"""
    try:
        devices = []
        
        # Try to get info from /sys/bus/usb/devices/
        usb_devices_path = "/sys/bus/usb/devices"
        if os.path.exists(usb_devices_path):
            device_dirs = [d for d in os.listdir(usb_devices_path) 
                        if re.match(r'\d+-\d+', d)]  # Format like 1-1, 2-1.1, etc.
            
            for device_dir in sorted(device_dirs):
                device_path = os.path.join(usb_devices_path, device_dir)
                device_info = {"Device Path": device_dir}
                
                # Read device attributes
                attributes = {
                    "idVendor": "Vendor ID",
                    "idProduct": "Product ID",
                    "manufacturer": "Manufacturer",
                    "product": "Product",
                    "serial": "Serial Number",
                    "version": "USB Version",
                    "bDeviceClass": "Device Class",
                    "bMaxPacketSize0": "Max Packet Size"
                }
                
                for attr_file, attr_name in attributes.items():
                    attr_path = os.path.join(device_path, attr_file)
                    try:
                        if os.path.exists(attr_path):
                            with open(attr_path, "r") as f:
                                value = f.read().strip()
                                if value and value != "00":
                                    device_info[attr_name] = value
                    except:
                        continue
                
                # Only add if we got some useful info
                if len(device_info) > 1:
                    devices.append(device_info)
        
        return devices if devices else [{"Error": "No USB information available. Install usbutils package for lsusb."}]
        
    except Exception as e:
        return [{"Error": f"Could not get USB devices fallback info: {str(e)}"}]

def get_usb_controllers_info():
    """Get USB controller information using lspci"""
    try:
        result = subprocess.run(
            ["lspci", "-v"],
            capture_output=True, text=True, check=True,
            env={**os.environ, "LC_ALL": "C"}
        )
        
        controllers = []
        current_controller = None
        in_usb_section = False
        
        for line in result.stdout.splitlines():
            line = line.strip()
            
            # Look for USB controllers
            if ("USB controller" in line or 
                "USB Controller" in line or
                "Host controller" in line):
                
                if current_controller:
                    controllers.append(current_controller)
                
                current_controller = {"Description": line}
                in_usb_section = True
                
            elif in_usb_section and current_controller and line:
                if line.startswith("Subsystem:"):
                    current_controller["Subsystem"] = line.split(": ", 1)[1] if ": " in line else line[10:]
                elif line.startswith("Kernel driver in use:"):
                    current_controller["Driver"] = line.split(": ", 1)[1] if ": " in line else line[21:]
                elif line.startswith("Kernel modules:"):
                    current_controller["Kernel Modules"] = line.split(": ", 1)[1] if ": " in line else line[15:]
                elif not line.startswith("\t") and ":" in line and not line.startswith("Flags:"):
                    # New device section started
                    in_usb_section = False
        
        # Add the last controller
        if current_controller:
            controllers.append(current_controller)
        
        return controllers if controllers else get_usb_controllers_fallback()
        
    except subprocess.CalledProcessError:
        return get_usb_controllers_fallback()
    except FileNotFoundError:
        return get_usb_controllers_fallback()
    except Exception as e:
        return [{"Error": f"Could not get USB controllers info: {str(e)}"}]

def get_usb_controllers_fallback():
    """Fallback method to get USB controller info"""
    try:
        controllers = []
        
        # Try to get info from /sys/bus/pci/devices/
        pci_devices_path = "/sys/bus/pci/devices"
        if os.path.exists(pci_devices_path):
            for device_dir in os.listdir(pci_devices_path):
                device_path = os.path.join(pci_devices_path, device_dir)
                class_file = os.path.join(device_path, "class")
                
                try:
                    if os.path.exists(class_file):
                        with open(class_file, "r") as f:
                            device_class = f.read().strip()
                            
                        # USB controller classes (0x0c03xx)
                        if device_class.startswith("0x0c03"):
                            controller = {"Device": device_dir}
                            
                            # Get vendor and device IDs
                            for id_file in ["vendor", "device"]:
                                id_path = os.path.join(device_path, id_file)
                                try:
                                    if os.path.exists(id_path):
                                        with open(id_path, "r") as f:
                                            value = f.read().strip()
                                            controller[f"{id_file.title()} ID"] = value
                                except:
                                    continue
                            
                            controllers.append(controller)
                            
                except:
                    continue
        
        return controllers if controllers else [{"Status": "No USB controller information available"}]
        
    except Exception as e:
        return [{"Error": f"Could not get USB controllers fallback info: {str(e)}"}]