import platform
import socket
import os
import time
import subprocess
import re
from datetime import datetime, timedelta

def get_os_info():
    """Get comprehensive operating system information including details and runtime info"""
    system_info = get_system_info()
    kernel_info = get_kernel_info()
    runtime_info = get_runtime_info()
    distribution_info = get_distribution_info()
    
    return {
        "System": system_info,
        "Kernel": kernel_info,
        "Distribution": distribution_info,
        "Runtime": runtime_info
    }

def get_system_info():
    """Get basic system information using platform module"""
    try:
        uname = platform.uname()
        
        system_data = {
            "OS": uname.system,
            "Release": uname.release,
            "Version": uname.version,
            "Architecture": uname.machine,
            "Processor": uname.processor if uname.processor else platform.processor(),
            "Hostname": socket.gethostname(),
            "Platform": platform.platform()
        }
        
        try:
            system_data["Python Version"] = platform.python_version()
        except:
            pass
        
        return system_data
        
    except Exception as e:
        return {"Error": f"Could not get system info: {str(e)}"}

def get_kernel_info():
    """Get detailed kernel information"""
    try:
        kernel_data = {}
        
        # Get kernel version from uname
        uname = platform.uname()
        kernel_data["Version"] = uname.release
        kernel_data["Build"] = uname.version
        
        try:
            with open("/proc/version", "r") as f:
                proc_version = f.read().strip()
                kernel_data["Full Version"] = proc_version
                
                gcc_match = re.search(r"gcc version ([^\)]+)", proc_version)
                if gcc_match:
                    kernel_data["Compiled with"] = f"GCC {gcc_match.group(1)}"
        except:
            pass
        
        try:
            with open("/proc/cmdline", "r") as f:
                cmdline = f.read().strip()
                # Truncate if too long
                if len(cmdline) > 100:
                    kernel_data["Command Line"] = cmdline[:100] + "..."
                else:
                    kernel_data["Command Line"] = cmdline
        except:
            pass
        try:
            with open("/proc/modules", "r") as f:
                modules_count = len(f.readlines())
                kernel_data["Loaded Modules"] = str(modules_count)
        except:
            pass
        
        return kernel_data if kernel_data else {"Error": "Could not get kernel info"}
        
    except Exception as e:
        return {"Error": f"Could not get kernel info: {str(e)}"}

def get_distribution_info():
    """Get Linux distribution information"""
    try:
        dist_data = {}
        
        # Try to get info from /etc/os-release (modern approach)
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        value = value.strip('"')
                        
                        if key == "NAME":
                            dist_data["Name"] = value
                        elif key == "VERSION":
                            dist_data["Version"] = value
                        elif key == "VERSION_ID":
                            dist_data["Version ID"] = value
                        elif key == "ID":
                            dist_data["ID"] = value
                        elif key == "ID_LIKE":
                            dist_data["Based On"] = value
                        elif key == "PRETTY_NAME":
                            dist_data["Pretty Name"] = value
                        elif key == "VERSION_CODENAME":
                            dist_data["Codename"] = value
        except:
            pass
        
        if not dist_data:
            try:
                with open("/etc/lsb-release", "r") as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            value = value.strip('"')
                            
                            if key == "DISTRIB_DESCRIPTION":
                                dist_data["Description"] = value
                            elif key == "DISTRIB_ID":
                                dist_data["ID"] = value
                            elif key == "DISTRIB_RELEASE":
                                dist_data["Release"] = value
                            elif key == "DISTRIB_CODENAME":
                                dist_data["Codename"] = value
            except:
                pass
        
        if not dist_data:
            try:
                if hasattr(platform, 'linux_distribution'):
                    linux_dist = platform.linux_distribution()
                    if linux_dist[0]:
                        dist_data["Name"] = linux_dist[0]
                        dist_data["Version"] = linux_dist[1]
                        dist_data["Codename"] = linux_dist[2]
            except:
                pass
        
        if not dist_data:
            try:
                result = subprocess.run(
                    ["lsb_release", "-a"],
                    capture_output=True, text=True, check=True,
                    env={**os.environ, "LC_ALL": "C"}
                )
                
                for line in result.stdout.splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == "Distributor ID":
                            dist_data["ID"] = value
                        elif key == "Description":
                            dist_data["Description"] = value
                        elif key == "Release":
                            dist_data["Release"] = value
                        elif key == "Codename":
                            dist_data["Codename"] = value
            except:
                pass
        
        return dist_data if dist_data else {"Warning": "Distribution information not available"}
        
    except Exception as e:
        return {"Error": f"Could not get distribution info: {str(e)}"}

def get_runtime_info():
    """Get system runtime information"""
    try:
        runtime_data = {}
        
        # Get uptime
        try:
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.read().split()[0])
                uptime_delta = timedelta(seconds=int(uptime_seconds))
                runtime_data["Uptime"] = str(uptime_delta)
                
                boot_time = datetime.now() - uptime_delta
                runtime_data["Boot Time"] = boot_time.strftime("%Y-%m-%d %H:%M:%S")
        except:
            try:
                boot_time = time.time() - os.sysconf('SC_CLK_TCK') * os.times().elapsed
                uptime = time.time() - boot_time
                runtime_data["Uptime (approx)"] = str(timedelta(seconds=int(uptime)))
            except:
                pass
        
        # Get load average
        try:
            with open("/proc/loadavg", "r") as f:
                loadavg = f.read().strip().split()
                runtime_data["Load Average"] = f"{loadavg[0]} {loadavg[1]} {loadavg[2]}"
        except:
            try:
                loadavg = os.getloadavg()
                runtime_data["Load Average"] = f"{loadavg[0]:.2f} {loadavg[1]:.2f} {loadavg[2]:.2f}"
            except:
                pass
        
        # Get number of processes
        try:
            with open("/proc/loadavg", "r") as f:
                loadavg_line = f.read().strip()
                processes_part = loadavg_line.split()[3]
                if "/" in processes_part:
                    running, total = processes_part.split("/")
                    runtime_data["Processes"] = f"{running} running / {total} total"
        except:
            pass
        
        # Get system timezone
        try:
            with open("/etc/timezone", "r") as f:
                timezone = f.read().strip()
                runtime_data["Timezone"] = timezone
        except:
            try:
                result = subprocess.run(
                    ["timedatectl", "show", "--property=Timezone", "--value"],
                    capture_output=True, text=True, check=True
                )
                if result.stdout.strip():
                    runtime_data["Timezone"] = result.stdout.strip()
            except:
                pass
        
        # Get current date/time
        current_time = datetime.now()
        runtime_data["Current Time"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return runtime_data if runtime_data else {"Error": "Could not get runtime info"}
        
    except Exception as e:
        return {"Error": f"Could not get runtime info: {str(e)}"}

def get_environment_info():
    """Get environment information (users, sessions, etc.)"""
    try:
        env_data = {}
        
        # Get current user
        try:
            env_data["Current User"] = os.getenv("USER") or os.getenv("USERNAME") or "Unknown"
        except:
            pass
        
        # Get logged in users
        try:
            result = subprocess.run(
                ["who"],
                capture_output=True, text=True, check=True
            )
            
            users = []
            for line in result.stdout.splitlines():
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        users.append(f"{parts[0]} ({parts[1]})")
            
            if users:
                env_data["Logged Users"] = users[:5]  
                
        except:
            pass
        

        try:
            shell = os.getenv("SHELL")
            if shell:
                env_data["Default Shell"] = os.path.basename(shell)
        except:
            pass
        
        return env_data if env_data else {"Status": "Environment information not available"}
        
    except Exception as e:
        return {"Error": f"Could not get environment info: {str(e)}"}