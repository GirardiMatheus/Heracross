import psutil
import subprocess
import re
import os
import argparse

def get_disk_info(include_partitions: bool = True):
    """
    Get physical disk hardware info.
    Optionally include partition usage info if include_partitions=True.
    """
    hardware_info = get_physical_disks_info()
    result = {
        "Hardware": hardware_info
    }
    if include_partitions:
        partitions_info = get_partitions_info()
        result["Partitions"] = partitions_info
    return result

def get_physical_disks_info():
    """Get info about physical disks (model, serial, size, type) using lsblk and udevadm"""
    disks = []
    try:
        lsblk_output = subprocess.run(
            ["lsblk", "-d", "-o", "NAME,MODEL,SIZE,ROTA,SERIAL,TYPE", "-P"], 
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "LC_ALL": "C"}
        ).stdout.splitlines()
        for line in lsblk_output:
            # Parse key="value" pairs
            fields = dict(re.findall(r'(\w+)="([^"]*)"', line))
            if fields.get("TYPE") != "disk":
                continue
            size = fields.get("SIZE", "").replace(",", ".")
            disk_info = {
                "Name": fields.get("NAME"),
                "Model": fields.get("MODEL"),
                "Vendor": get_disk_vendor(fields.get("NAME")),
                "Serial": fields.get("SERIAL"),
                "Size": size,
                "Type": "SSD" if fields.get("ROTA") == "0" else "HDD" if fields.get("ROTA") == "1" else fields.get("TYPE"),
            }
            disks.append(disk_info)
        if not disks:
            disks.append({"Warning": "No physical disks found. Check lsblk output or permissions."})
    except Exception as e:
        disks.append({"Error": f"Could not get disk hardware info: {str(e)}"})
    return disks

def get_disk_vendor(disk_name):
    """Try to get disk vendor using udevadm"""
    try:
        dev_path = f"/dev/{disk_name}"
        output = subprocess.run(
            ["udevadm", "info", "--query=property", "--name", dev_path],
            capture_output=True, text=True
        ).stdout
        for line in output.splitlines():
            if line.startswith("ID_VENDOR="):
                return line.split("=", 1)[1]
    except Exception:
        pass
    return None

def get_partitions_info():
    """Get info about mounted partitions and their usage"""
    partitions = psutil.disk_partitions()
    partition_data = []
    for p in partitions:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            partition_data.append({
                "Device": p.device,
                "Mountpoint": p.mountpoint,
                "File system": p.fstype,
                "Total": f"{usage.total / (1024 ** 3):.2f} GB",
                "Used": f"{usage.used / (1024 ** 3):.2f} GB",
                "Free": f"{usage.free / (1024 ** 3):.2f} GB",
                "Usage Percent": f"{usage.percent}%",
                "Options": p.opts
            })
        except PermissionError:
            continue
    return partition_data

