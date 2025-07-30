import subprocess
import re
import os

def get_gpu_info():
    """Get comprehensive GPU information including hardware details and driver info"""
    hardware_info = get_gpu_hardware_info()
    driver_info = get_gpu_driver_info()
    temperature_info = get_gpu_temperature()
    
    return {
        "Hardware": hardware_info,
        "Drivers": driver_info,
        "Temperature": temperature_info
    }

def get_gpu_hardware_info():
    """Get GPU hardware information using lspci and additional sources"""
    gpus = []
    
    try:
        # Get basic GPU info from lspci
        result = subprocess.run(
            ["lspci", "-v"], 
            capture_output=True, text=True, check=True,
            env={**os.environ, "LC_ALL": "C"}
        )
        output = result.stdout
        
        # Parse lspci output for GPU devices
        current_gpu = {}
        in_gpu_section = False
        
        for line in output.splitlines():
            line = line.strip()
            
            # Detect GPU devices
            if ("VGA compatible controller" in line or 
                "3D controller" in line or 
                "Display controller" in line):
                
                if current_gpu:  # Save previous GPU
                    gpus.append(current_gpu)
                
                # Start new GPU
                current_gpu = {}
                in_gpu_section = True
                
                # Extract basic info from the device line
                parts = line.split(": ", 1)
                if len(parts) > 1:
                    device_info = parts[1]
                    current_gpu["Device"] = device_info
                    
                    # Try to extract vendor and model
                    if " " in device_info:
                        vendor_model = device_info.split(" ", 1)
                        current_gpu["Vendor"] = vendor_model[0]
                        if len(vendor_model) > 1:
                            current_gpu["Model"] = vendor_model[1]
                
            elif in_gpu_section and line:
                if line.startswith("Subsystem:"):
                    current_gpu["Subsystem"] = line.split(": ", 1)[1] if ": " in line else line[10:]
                elif line.startswith("Kernel driver in use:"):
                    current_gpu["Driver"] = line.split(": ", 1)[1] if ": " in line else line[21:]
                elif line.startswith("Kernel modules:"):
                    current_gpu["Kernel Modules"] = line.split(": ", 1)[1] if ": " in line else line[15:]
                elif not line.startswith("\t") and ":" in line:
                    # New device section started
                    in_gpu_section = False
        
        # Add the last GPU if exists
        if current_gpu:
            gpus.append(current_gpu)
        
        # Enhance with additional info
        gpus = enhance_gpu_info(gpus)
        
        return gpus if gpus else [{"Warning": "No GPU devices found"}]
        
    except subprocess.CalledProcessError as e:
        return [{"Error": f"lspci command failed: {str(e)}"}]
    except FileNotFoundError:
        return get_gpu_fallback_info()
    except Exception as e:
        return [{"Error": f"Could not get GPU hardware info: {str(e)}"}]

def enhance_gpu_info(gpus):
    """Enhance GPU information with additional details"""
    for gpu in gpus:
        # Try to get memory info for NVIDIA cards
        if "NVIDIA" in gpu.get("Vendor", "").upper() or "NVIDIA" in gpu.get("Device", "").upper():
            memory_info = get_nvidia_memory_info()
            if memory_info:
                gpu.update(memory_info)
        
        # Try to get memory info for AMD cards
        elif "AMD" in gpu.get("Vendor", "").upper() or "ATI" in gpu.get("Vendor", "").upper():
            memory_info = get_amd_memory_info()
            if memory_info:
                gpu.update(memory_info)
    
    return gpus

def get_nvidia_memory_info():
    """Get NVIDIA GPU memory information using nvidia-smi"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True
        )
        
        lines = result.stdout.strip().splitlines()
        if lines:
            # Take first GPU info
            memory_data = lines[0].split(", ")
            if len(memory_data) >= 3:
                return {
                    "Memory Total": f"{memory_data[0]} MB",
                    "Memory Used": f"{memory_data[1]} MB",
                    "Memory Free": f"{memory_data[2]} MB"
                }
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return {}

def get_amd_memory_info():
    """Get AMD GPU memory information"""
    try:
        # Try rocm-smi for AMD cards
        result = subprocess.run(
            ["rocm-smi", "--showmeminfo", "vram"],
            capture_output=True, text=True, check=True
        )
        
        # Parse rocm-smi output (basic implementation)
        if "VRAM" in result.stdout:
            return {"Memory Info": "Available via rocm-smi"}
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return {}

def get_gpu_fallback_info():
    """Fallback method to get GPU info without lspci"""
    try:
        gpus = []
        
        # Try to get info from /proc/driver/nvidia/version
        nvidia_file = "/proc/driver/nvidia/version"
        if os.path.exists(nvidia_file):
            try:
                with open(nvidia_file, "r") as f:
                    content = f.read()
                    gpus.append({
                        "Type": "NVIDIA GPU detected",
                        "Driver Info": content.strip().split('\n')[0] if content.strip() else "Unknown"
                    })
            except:
                pass
        
        # Try to get info from /sys/class/drm/
        drm_path = "/sys/class/drm"
        if os.path.exists(drm_path):
            try:
                drm_devices = os.listdir(drm_path)
                card_devices = [d for d in drm_devices if d.startswith("card") and not "-" in d]
                
                for card in card_devices:
                    card_path = os.path.join(drm_path, card, "device")
                    if os.path.exists(card_path):
                        try:
                            vendor_path = os.path.join(card_path, "vendor")
                            device_path = os.path.join(card_path, "device")
                            
                            vendor_id = ""
                            device_id = ""
                            
                            if os.path.exists(vendor_path):
                                with open(vendor_path, "r") as f:
                                    vendor_id = f.read().strip()
                            
                            if os.path.exists(device_path):
                                with open(device_path, "r") as f:
                                    device_id = f.read().strip()
                            
                            if vendor_id or device_id:
                                gpus.append({
                                    "Card": card,
                                    "Vendor ID": vendor_id,
                                    "Device ID": device_id
                                })
                        except:
                            continue
            except:
                pass
        
        return gpus if gpus else [{"Error": "No GPU information available. Install lspci (pciutils package)."}]
        
    except Exception as e:
        return [{"Error": f"Could not get GPU fallback info: {str(e)}"}]

def get_gpu_driver_info():
    """Get GPU driver information"""
    drivers = {}
    
    # Check for NVIDIA driver
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, check=True
        )
        if result.stdout.strip():
            drivers["NVIDIA Driver"] = result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Check for AMD driver (amdgpu)
    try:
        modinfo_result = subprocess.run(
            ["modinfo", "amdgpu"],
            capture_output=True, text=True, check=True
        )
        if modinfo_result.stdout:
            for line in modinfo_result.stdout.splitlines():
                if line.startswith("version:"):
                    drivers["AMD Driver (amdgpu)"] = line.split(":", 1)[1].strip()
                    break
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Check for Intel driver (i915)
    try:
        modinfo_result = subprocess.run(
            ["modinfo", "i915"],
            capture_output=True, text=True, check=True
        )
        if modinfo_result.stdout:
            drivers["Intel Driver (i915)"] = "Available"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return drivers if drivers else {"Status": "No specific GPU drivers detected"}

def get_gpu_temperature():
    """Get GPU temperature information"""
    temperatures = {}
    
    # Try NVIDIA temperature
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True
        )
        
        lines = result.stdout.strip().splitlines()
        for i, temp in enumerate(lines):
            if temp.strip():
                temperatures[f"NVIDIA GPU {i+1}"] = f"{temp.strip()}°C"
                
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try AMD temperature via sensors
    try:
        result = subprocess.run(["sensors"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if "amdgpu" in line.lower() or "radeon" in line.lower():
                if "°C" in line and ":" in line:
                    sensor_name = line.split(":")[0].strip()
                    temp_part = line.split(":")[1].strip()
                    if temp_part:
                        temperatures[f"AMD {sensor_name}"] = temp_part.split()[0]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try generic GPU temperature from hwmon
    try:
        hwmon_path = "/sys/class/hwmon"
        if os.path.exists(hwmon_path):
            for hwmon_dir in os.listdir(hwmon_path):
                hwmon_full_path = os.path.join(hwmon_path, hwmon_dir)
                name_file = os.path.join(hwmon_full_path, "name")
                
                if os.path.exists(name_file):
                    try:
                        with open(name_file, "r") as f:
                            name = f.read().strip()
                        
                        if any(gpu_name in name.lower() for gpu_name in ["amdgpu", "radeon", "nouveau"]):
                            # Look for temperature files
                            for file in os.listdir(hwmon_full_path):
                                if file.startswith("temp") and file.endswith("_input"):
                                    temp_file = os.path.join(hwmon_full_path, file)
                                    try:
                                        with open(temp_file, "r") as f:
                                            temp_raw = int(f.read().strip())
                                            temp_celsius = temp_raw / 1000.0
                                            temperatures[f"{name} {file}"] = f"{temp_celsius:.1f}°C"
                                    except:
                                        continue
                    except:
                        continue
    except:
        pass
    
    return temperatures if temperatures else {"Status": "GPU temperature sensors not available"}