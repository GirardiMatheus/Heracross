import subprocess
import re
import os
import json

def get_network_info(include_details=False):
    """Get comprehensive network information including hardware details and interface status"""
    hardware_info = get_network_hardware_info()
    interface_info = get_network_interface_info(include_details)
    connection_info = get_network_connection_info()
    
    return {
        "Hardware": hardware_info,
        "Interfaces": interface_info,
        "Connections": connection_info
    }

def get_network_hardware_info():
    """Get network hardware information using lshw and fallback methods"""
    try:
        result = subprocess.run(
            ["lshw", "-C", "network", "-json"],
            capture_output=True, text=True, check=True,
            env={**os.environ, "LC_ALL": "C"}
        )
        
        # Try JSON output first
        try:
            data = json.loads(result.stdout)
            if not isinstance(data, list):
                data = [data]
            
            adapters = []
            for item in data:
                adapter = parse_lshw_json_item(item)
                if adapter:
                    adapters.append(adapter)
            
            return adapters if adapters else get_network_hardware_fallback()
            
        except json.JSONDecodeError:
            # Fallback to text parsing
            return parse_lshw_text_output(result.stdout)
            
    except subprocess.CalledProcessError:
        return get_network_hardware_fallback()
    except FileNotFoundError:
        return get_network_hardware_fallback()
    except Exception as e:
        return [{"Error": f"Could not get network hardware info: {str(e)}"}]

def parse_lshw_json_item(item):
    """Parse a single network item from lshw JSON output"""
    if item.get("class") != "network":
        return None
    
    adapter = {
        "Description": item.get("description", "N/A"),
        "Product": item.get("product", "N/A"),
        "Vendor": item.get("vendor", "N/A"),
        "Interface": item.get("logicalname", "N/A"),
        "MAC Address": item.get("serial", "N/A")
    }
    
    # Get configuration details
    config = item.get("configuration", {})
    if config:
        if "driver" in config:
            adapter["Driver"] = config["driver"]
        if "link" in config:
            adapter["Link Status"] = config["link"]
        if "speed" in config:
            adapter["Speed"] = config["speed"]
    
    return adapter

def parse_lshw_text_output(output):
    """Parse lshw text output as fallback"""
    adapters = output.strip().split("*-network")
    parsed = []
    
    for adapter in adapters[1:]:  # Skip first empty section
        name = re.search(r"description:\s*(.+)", adapter)
        logical = re.search(r"logical name:\s*(.+)", adapter)
        mac = re.search(r"serial:\s*(.+)", adapter)
        product = re.search(r"product:\s*(.+)", adapter)
        vendor = re.search(r"vendor:\s*(.+)", adapter)
        driver = re.search(r"driver=([^\s]+)", adapter)
        
        parsed.append({
            "Description": name.group(1).strip() if name else "N/A",
            "Product": product.group(1).strip() if product else "N/A",
            "Vendor": vendor.group(1).strip() if vendor else "N/A",
            "Interface": logical.group(1).strip() if logical else "N/A",
            "MAC Address": mac.group(1).strip() if mac else "N/A",
            "Driver": driver.group(1).strip() if driver else "N/A"
        })
    
    return parsed if parsed else get_network_hardware_fallback()

def get_network_hardware_fallback():
    """Fallback method to get network hardware info without lshw"""
    try:
        adapters = []
        
        # Try to get info from /sys/class/net/
        net_path = "/sys/class/net"
        if os.path.exists(net_path):
            interfaces = os.listdir(net_path)
            
            for interface in interfaces:
                if interface == "lo":  # Skip loopback
                    continue
                
                interface_path = os.path.join(net_path, interface)
                adapter = {"Interface": interface}
                
                # Get MAC address
                try:
                    with open(os.path.join(interface_path, "address"), "r") as f:
                        adapter["MAC Address"] = f.read().strip()
                except:
                    adapter["MAC Address"] = "N/A"
                
                # Get driver info
                try:
                    driver_link = os.path.join(interface_path, "device/driver")
                    if os.path.islink(driver_link):
                        driver_name = os.path.basename(os.readlink(driver_link))
                        adapter["Driver"] = driver_name
                except:
                    adapter["Driver"] = "N/A"
                
                adapters.append(adapter)
        
        return adapters if adapters else [{"Error": "No network hardware information available. Install lshw package."}]
        
    except Exception as e:
        return [{"Error": f"Could not get network hardware fallback info: {str(e)}"}]

def get_network_interface_info(include_details=False):
    """Get network interface status and configuration using ip command"""
    try:
        result = subprocess.run(
            ["ip", "-json", "addr", "show"],
            capture_output=True, text=True, check=True,
            env={**os.environ, "LC_ALL": "C"}
        )
        
        try:
            interfaces_data = json.loads(result.stdout)
            interfaces = []
            
            for iface in interfaces_data:
                interface_name = iface.get("ifname", "N/A")
                state = iface.get("operstate", "N/A")
                
                # Filter interfaces in summary mode
                if not include_details:
                    # Skip virtual/docker interfaces and show only main physical interfaces
                    if (interface_name.startswith(("br-", "veth", "docker")) or 
                        state == "DOWN" and interface_name != "lo"):
                        continue
                
                interface = {
                    "Interface": interface_name,
                    "State": state,
                    "Type": iface.get("link_type", "N/A")
                }
                
                # Get IP addresses
                ip_addresses = []
                for addr_info in iface.get("addr_info", []):
                    if addr_info.get("family") in ["inet", "inet6"]:
                        ip_addr = f"{addr_info.get('local', '')}/{addr_info.get('prefixlen', '')}"
                        ip_addresses.append(ip_addr)
                
                if ip_addresses:
                    if include_details:
                        interface["IP Addresses"] = ip_addresses
                    else:
                        # Show only primary IPv4 in summary
                        ipv4_addrs = [addr for addr in ip_addresses if ":" not in addr.split("/")[0]]
                        if ipv4_addrs:
                            interface["Primary IP"] = ipv4_addrs[0]
                
                # Add additional details only if requested
                if include_details:
                    interface["MTU"] = iface.get("mtu", "N/A")
                    flags = iface.get("flags", [])
                    if flags:
                        interface["Flags"] = ", ".join(flags)
                
                interfaces.append(interface)
            
            return interfaces
            
        except json.JSONDecodeError:
            return get_interface_info_fallback(include_details)
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        return get_interface_info_fallback(include_details)
    except Exception as e:
        return [{"Error": f"Could not get interface info: {str(e)}"}]

def get_interface_info_fallback(include_details=False):
    """Fallback method to get interface info using ifconfig or /proc/net/dev"""
    try:
        # Try ifconfig first
        try:
            result = subprocess.run(
                ["ifconfig"],
                capture_output=True, text=True, check=True
            )
            return parse_ifconfig_output(result.stdout, include_details)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Fallback to /proc/net/dev
        try:
            with open("/proc/net/dev", "r") as f:
                lines = f.readlines()
            
            interfaces = []
            for line in lines[2:]:  # Skip header lines
                parts = line.strip().split()
                if parts:
                    interface_name = parts[0].rstrip(":")
                    if interface_name != "lo":  # Skip loopback
                        interface = {
                            "Interface": interface_name,
                            "Status": "Available"
                        }
                        
                        if include_details:
                            interface["RX Bytes"] = parts[1]
                            interface["TX Bytes"] = parts[9]
                        
                        interfaces.append(interface)
            
            return interfaces if interfaces else [{"Warning": "No network interfaces found"}]
            
        except Exception:
            return [{"Error": "Could not get interface information"}]
            
    except Exception as e:
        return [{"Error": f"Could not get interface fallback info: {str(e)}"}]

def parse_ifconfig_output(output, include_details=False):
    """Parse ifconfig output"""
    interfaces = []
    current_interface = None
    
    for line in output.splitlines():
        if line and not line.startswith(" "):
            # New interface
            if current_interface:
                interfaces.append(current_interface)
            
            interface_name = line.split()[0]
            if interface_name != "lo":  # Skip loopback
                current_interface = {"Interface": interface_name}
                
                # Extract flags only if details requested
                if include_details:
                    flags_match = re.search(r"flags=\d+<([^>]+)>", line)
                    if flags_match:
                        current_interface["Flags"] = flags_match.group(1)
        
        elif current_interface and "inet" in line:
            # IP address line
            inet_match = re.search(r"inet (\S+)", line)
            if inet_match:
                if include_details:
                    current_interface["IP Address"] = inet_match.group(1)
                else:
                    current_interface["Primary IP"] = inet_match.group(1)
        
        elif current_interface and "ether" in line and include_details:
            # MAC address line (only in details mode)
            ether_match = re.search(r"ether (\S+)", line)
            if ether_match:
                current_interface["MAC Address"] = ether_match.group(1)
    
    if current_interface:
        interfaces.append(current_interface)
    
    return interfaces if interfaces else [{"Warning": "No network interfaces found"}]

def get_network_connection_info():
    """Get network connection and routing information"""
    try:
        connections = {}
        
        # Get default route
        try:
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                connections["Default Gateway"] = result.stdout.strip().split()[2]
        except:
            pass
        
        # Get DNS servers
        try:
            with open("/etc/resolv.conf", "r") as f:
                dns_servers = []
                for line in f:
                    if line.startswith("nameserver"):
                        dns_servers.append(line.split()[1])
                if dns_servers:
                    connections["DNS Servers"] = dns_servers[:3]  # Limit to 3
        except:
            pass
        
        return connections if connections else {"Status": "No connection information available"}
        
    except Exception as e:
        return {"Error": f"Could not get connection info: {str(e)}"}