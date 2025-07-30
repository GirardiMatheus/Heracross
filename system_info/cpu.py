import subprocess
import os

def get_cpu_info():
    """Get comprehensive CPU information including hardware details and current status"""
    basic_info = get_basic_cpu_info()
    detailed_info = get_detailed_cpu_info()
    temperature_info = get_cpu_temperature()
    frequency_info = get_cpu_frequencies()
    
    return {
        "Basic Info": basic_info,
        "Hardware Details": detailed_info,
        "Temperature": temperature_info,
        "Current Frequencies": frequency_info
    }

def get_basic_cpu_info():
    """Get basic CPU information from lscpu"""
    try:
        output = subprocess.run(["lscpu"], capture_output=True, text=True)
        info = {}
        for line in output.stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        
        return {
            "Model": info.get("Model name"),
            "Architecture": info.get("Architecture"),
            "Vendor": info.get("Vendor ID"),
            "CPU Family": info.get("CPU family"),
            "Model Number": info.get("Model"),
            "Stepping": info.get("Stepping"),
            "Cores (physical)": info.get("Core(s) per socket"),
            "Threads (logical)": info.get("CPU(s)"),
            "Sockets": info.get("Socket(s)"),
            "Max MHz": info.get("CPU max MHz"),
            "Min MHz": info.get("CPU min MHz"),
            "Current MHz": info.get("CPU MHz"),
            "Cache L1d": info.get("L1d cache"),
            "Cache L1i": info.get("L1i cache"),
            "Cache L2": info.get("L2 cache"),
            "Cache L3": info.get("L3 cache"),
        }
    except Exception as e:
        return {"Error": f"Could not get basic CPU info: {str(e)}"}

def get_detailed_cpu_info():
    """Get detailed CPU information from /proc/cpuinfo"""
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
        
        # Parse the first processor entry for detailed info
        processor_info = {}
        for line in cpuinfo.splitlines():
            if line.strip() == "":
                break  
            if ":" in line:
                key, value = line.split(":", 1)
                processor_info[key.strip()] = value.strip()
        
        return {
            "Processor": processor_info.get("processor", "0"),
            "Vendor ID": processor_info.get("vendor_id"),
            "CPU Family": processor_info.get("cpu family"),
            "Model": processor_info.get("model"),
            "Model Name": processor_info.get("model name"),
            "Stepping": processor_info.get("stepping"),
            "Microcode": processor_info.get("microcode"),
            "CPU MHz": processor_info.get("cpu MHz"),
            "Cache Size": processor_info.get("cache size"),
            "Physical ID": processor_info.get("physical id"),
            "Siblings": processor_info.get("siblings"),
            "Core ID": processor_info.get("core id"),
            "CPU Cores": processor_info.get("cpu cores"),
            "Flags": processor_info.get("flags", "").split()[:10] if processor_info.get("flags") else []  # First 10 flags
        }
    except Exception as e:
        return {"Error": f"Could not get detailed CPU info: {str(e)}"}

def get_cpu_temperature():
    """Get CPU temperature information"""
    temperatures = {}
    
    # Try multiple sources for temperature
    temp_sources = [
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/class/thermal/thermal_zone1/temp",
        "/sys/class/thermal/thermal_zone2/temp"
    ]
    
    for i, temp_file in enumerate(temp_sources):
        try:
            if os.path.exists(temp_file):
                with open(temp_file, "r") as f:
                    temp_raw = int(f.read().strip())
                    temp_celsius = temp_raw / 1000.0
                    temperatures[f"Zone {i}"] = f"{temp_celsius:.1f}°C"
        except:
            continue
    
    # Try sensors command as alternative
    if not temperatures:
        try:
            output = subprocess.run(["sensors"], capture_output=True, text=True)
            if output.returncode == 0:
                for line in output.stdout.splitlines():
                    if "Core" in line and "°C" in line:
                        temperatures[line.split(":")[0].strip()] = line.split(":")[1].strip().split()[0]
        except:
            pass
    
    return temperatures if temperatures else {"Status": "Temperature sensors not available"}

def get_cpu_frequencies():
    """Get current CPU frequencies for each core"""
    frequencies = {}
    
    try:
        scaling_path = "/sys/devices/system/cpu"
        cpu_dirs = [d for d in os.listdir(scaling_path) if d.startswith("cpu") and d[3:].isdigit()]
        
        for cpu_dir in sorted(cpu_dirs):
            cpu_num = cpu_dir[3:]
            freq_file = os.path.join(scaling_path, cpu_dir, "cpufreq/scaling_cur_freq")
            
            if os.path.exists(freq_file):
                try:
                    with open(freq_file, "r") as f:
                        freq_khz = int(f.read().strip())
                        freq_mhz = freq_khz / 1000
                        frequencies[f"CPU {cpu_num}"] = f"{freq_mhz:.0f} MHz"
                except:
                    continue
        
        # If no scaling frequencies, try cpuinfo_cur_freq
        if not frequencies:
            for cpu_dir in sorted(cpu_dirs):
                cpu_num = cpu_dir[3:]
                freq_file = os.path.join(scaling_path, cpu_dir, "cpufreq/cpuinfo_cur_freq")
                
                if os.path.exists(freq_file):
                    try:
                        with open(freq_file, "r") as f:
                            freq_khz = int(f.read().strip())
                            freq_mhz = freq_khz / 1000
                            frequencies[f"CPU {cpu_num}"] = f"{freq_mhz:.0f} MHz"
                    except:
                        continue
                        
    except Exception as e:
        frequencies["Error"] = f"Could not read frequencies: {str(e)}"
    
    return frequencies if frequencies else {"Status": "Frequency information not available"}

def get_cpu_usage():
    """Get current CPU usage percentage"""
    try:
        # Read /proc/stat for CPU usage
        with open("/proc/stat", "r") as f:
            line = f.readline()
        
        if line.startswith("cpu "):
            values = line.split()[1:]
            total_time = sum(int(v) for v in values)
            idle_time = int(values[3])
            
            # For a single measurement, we can't calculate percentage accurately
            # This would need two measurements with a time interval
            return {"Note": "Real-time usage calculation requires time interval measurement"}
    except:
        pass
    
    return {"Status": "CPU usage information not available"}