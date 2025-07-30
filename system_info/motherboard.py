import subprocess
import re
import os

def get_motherboard_info():
    """Get comprehensive motherboard information including hardware details and BIOS info"""
    motherboard_hardware = get_motherboard_hardware_info()
    bios_info = get_bios_info()
    system_info = get_system_info()
    
    return {
        "Motherboard": motherboard_hardware,
        "BIOS": bios_info,
        "System": system_info
    }

def get_motherboard_hardware_info():
    """Get motherboard hardware information using dmidecode"""
    try:
        result = subprocess.run(
            ["sudo", "dmidecode", "-t", "baseboard"],
            capture_output=True, text=True, check=True,
            env={**os.environ, "LC_ALL": "C"}
        )
        output = result.stdout
        
        motherboard_data = {}
        
        # Parse dmidecode output more robustly
        for line in output.splitlines():
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                
                if key == "Manufacturer" and value != "Not Specified":
                    motherboard_data["Manufacturer"] = value
                elif key == "Product Name" and value != "Not Specified":
                    motherboard_data["Product Name"] = value
                elif key == "Version" and value != "Not Specified":
                    motherboard_data["Version"] = value
                elif key == "Serial Number" and value != "Not Specified":
                    motherboard_data["Serial Number"] = value
                elif key == "Asset Tag" and value != "Not Specified":
                    motherboard_data["Asset Tag"] = value
                elif key == "Location In Chassis" and value != "Not Specified":
                    motherboard_data["Location In Chassis"] = value
        
        return motherboard_data if motherboard_data else {"Warning": "No motherboard information found"}
        
    except subprocess.CalledProcessError:
        return get_motherboard_fallback_info()
    except FileNotFoundError:
        return {"Error": "dmidecode command not found. Install dmidecode package."}
    except Exception as e:
        return {"Error": f"Could not get motherboard info: {str(e)}"}

def get_motherboard_fallback_info():
    """Fallback method to get motherboard info without sudo"""
    try:
        info = {}
        
        # Try to get info from /sys/class/dmi/id/
        dmi_paths = {
            "Manufacturer": "/sys/class/dmi/id/board_vendor",
            "Product Name": "/sys/class/dmi/id/board_name",
            "Version": "/sys/class/dmi/id/board_version",
            "Serial Number": "/sys/class/dmi/id/board_serial"
        }
        
        for key, path in dmi_paths.items():
            try:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        value = f.read().strip()
                        if value and value != "Not Specified":
                            info[key] = value
            except:
                continue
        
        if info:
            return info
        else:
            return {"Error": "Permission denied. Run with sudo for complete motherboard information."}
            
    except Exception as e:
        return {"Error": f"Could not get motherboard fallback info: {str(e)}"}

def get_bios_info():
    """Get BIOS information using dmidecode"""
    try:
        result = subprocess.run(
            ["sudo", "dmidecode", "-t", "bios"],
            capture_output=True, text=True, check=True,
            env={**os.environ, "LC_ALL": "C"}
        )
        output = result.stdout
        
        bios_data = {}
        
        # Parse dmidecode output more robustly
        for line in output.splitlines():
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                
                if key == "Vendor" and value != "Not Specified":
                    bios_data["Vendor"] = value
                elif key == "Version" and value != "Not Specified":
                    bios_data["Version"] = value
                elif key == "Release Date" and value != "Not Specified":
                    bios_data["Release Date"] = value
                elif key == "ROM Size" and value != "Not Specified":
                    bios_data["ROM Size"] = value
                elif key == "BIOS Revision" and value != "Not Specified":
                    bios_data["BIOS Revision"] = value
        
        return bios_data if bios_data else {"Warning": "No BIOS information found"}
        
    except subprocess.CalledProcessError:
        return get_bios_fallback_info()
    except FileNotFoundError:
        return {"Error": "dmidecode command not found. Install dmidecode package."}
    except Exception as e:
        return {"Error": f"Could not get BIOS info: {str(e)}"}

def get_bios_fallback_info():
    """Fallback method to get BIOS info without sudo"""
    try:
        info = {}
        
        # Try to get info from /sys/class/dmi/id/
        dmi_paths = {
            "Vendor": "/sys/class/dmi/id/bios_vendor",
            "Version": "/sys/class/dmi/id/bios_version",
            "Release Date": "/sys/class/dmi/id/bios_date"
        }
        
        for key, path in dmi_paths.items():
            try:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        value = f.read().strip()
                        if value and value != "Not Specified":
                            info[key] = value
            except:
                continue
        
        if info:
            return info
        else:
            return {"Error": "Permission denied. Run with sudo for complete BIOS information."}
            
    except Exception as e:
        return {"Error": f"Could not get BIOS fallback info: {str(e)}"}

def get_system_info():
    """Get general system information"""
    try:
        result = subprocess.run(
            ["sudo", "dmidecode", "-t", "system"],
            capture_output=True, text=True, check=True,
            env={**os.environ, "LC_ALL": "C"}
        )
        output = result.stdout
        
        system_data = {}
        
        # Parse dmidecode output
        for line in output.splitlines():
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                
                if key == "Manufacturer" and value != "Not Specified":
                    system_data["Manufacturer"] = value
                elif key == "Product Name" and value != "Not Specified":
                    system_data["Product Name"] = value
                elif key == "Version" and value != "Not Specified":
                    system_data["Version"] = value
                elif key == "Serial Number" and value != "Not Specified":
                    system_data["Serial Number"] = value
                elif key == "UUID" and value != "Not Specified":
                    system_data["UUID"] = value
                elif key == "Family" and value != "Not Specified":
                    system_data["Family"] = value
        
        return system_data if system_data else {"Warning": "No system information found"}
        
    except subprocess.CalledProcessError:
        return get_system_fallback_info()
    except FileNotFoundError:
        return {"Error": "dmidecode command not found. Install dmidecode package."}
    except Exception as e:
        return {"Error": f"Could not get system info: {str(e)}"}

def get_system_fallback_info():
    """Fallback method to get system info without sudo"""
    try:
        info = {}
        
        # Try to get info from /sys/class/dmi/id/
        dmi_paths = {
            "Manufacturer": "/sys/class/dmi/id/sys_vendor",
            "Product Name": "/sys/class/dmi/id/product_name",
            "Version": "/sys/class/dmi/id/product_version",
            "Serial Number": "/sys/class/dmi/id/product_serial",
            "UUID": "/sys/class/dmi/id/product_uuid",
            "Family": "/sys/class/dmi/id/product_family"
        }
        
        for key, path in dmi_paths.items():
            try:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        value = f.read().strip()
                        if value and value != "Not Specified":
                            info[key] = value
            except:
                continue
        
        if info:
            return info
        else:
            return {"Error": "Permission denied. Run with sudo for complete system information."}
            
    except Exception as e:
        return {"Error": f"Could not get system fallback info: {str(e)}"}