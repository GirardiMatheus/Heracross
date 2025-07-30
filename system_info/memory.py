import subprocess
import psutil

def get_memory_info():
    """Get both usage statistics and hardware information about RAM"""
    # Get usage statistics
    mem = psutil.virtual_memory()
    usage_info = {
        "Total": f"{mem.total / (1024 ** 3):.2f} GB",
        "Available": f"{mem.available / (1024 ** 3):.2f} GB",
        "Used": f"{mem.used / (1024 ** 3):.2f} GB",
        "Usage Percent": f"{mem.percent}%",
    }
    
    # Get hardware information
    hardware_info = get_memory_hardware_info()
    
    return {
        "Usage": usage_info,
        "Hardware": hardware_info
    }

def get_memory_hardware_info():
    """Get detailed hardware information about RAM modules"""
    try:
        output = subprocess.run(
            ["sudo", "dmidecode", "--type", "memory"], 
            capture_output=True, 
            text=True
        )
        
        if output.returncode != 0:
            return get_basic_memory_info()
        
        return parse_dmidecode_output(output.stdout)
    
    except (subprocess.SubprocessError, FileNotFoundError):
        return get_basic_memory_info()

def parse_dmidecode_output(output):
    """Parse dmidecode output to extract memory module information"""
    modules = []
    current_module = {}
    
    for line in output.splitlines():
        line = line.strip()
        
        if line.startswith("Memory Device"):
            if current_module:  
                modules.append(current_module)
            current_module = {}
        
        elif ":" in line and current_module is not None:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            # Map relevant fields
            if key == "Size" and value != "No Module Installed":
                current_module["Size"] = value
            elif key == "Manufacturer":
                current_module["Manufacturer"] = value
            elif key == "Part Number":
                current_module["Part Number"] = value
            elif key == "Speed":
                current_module["Speed"] = value
            elif key == "Type":
                current_module["Type"] = value
            elif key == "Locator":
                current_module["Slot"] = value
    
    if current_module:
        modules.append(current_module)
    
    installed_modules = [mod for mod in modules if mod.get("Size")]
    
    return {
        "Total Slots": len(modules),
        "Installed Modules": len(installed_modules),
        "Modules": installed_modules
    }

def get_basic_memory_info():
    """Fallback method using /proc/meminfo"""
    try:
        with open("/proc/meminfo", "r") as f:
            meminfo = f.read()
        
        info = {}
        for line in meminfo.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        
        return {
            "Total Memory": info.get("MemTotal", "Unknown"),
            "Note": "Detailed hardware info requires sudo privileges"
        }
    
    except Exception as e:
        return {"Error": f"Could not read memory information: {str(e)}"}

def get_memory_info_no_sudo():
    """Get memory information without requiring sudo privileges"""
    mem = psutil.virtual_memory()
    
    try:
        # Try to get some basic info from /sys/devices/system/memory/
        memory_info = {
            "Total": f"{mem.total / (1024 ** 3):.2f} GB",
            "Available": f"{mem.available / (1024 ** 3):.2f} GB",
            "Used": f"{mem.used / (1024 ** 3):.2f} GB",
            "Usage Percent": f"{mem.percent}%",
        }
        
        # Try to get memory block size
        try:
            with open("/sys/devices/system/memory/block_size_bytes", "r") as f:
                block_size = int(f.read().strip(), 16)
                memory_info["Block Size"] = f"{block_size / (1024 ** 2)} MB"
        except:
            pass
        
        return memory_info
    
    except Exception as e:
        return {"Error": f"Could not read memory information: {str(e)}"}