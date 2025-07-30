import argparse
from system_info import cpu, memory, disk, motherboard, gpu

def print_section(title, data, indent=0):
    """Helper function to print data sections with proper formatting"""
    prefix = "  " * indent
    print(f"{prefix}{title}:")
    
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                if v and isinstance(v[0], dict):
                    label = "Module" if k.lower().startswith("module") or k == "Modules" else \
                            "Partition" if k.lower().startswith("partition") or k == "Partitions" else \
                            "Disk" if k.lower().startswith("hardware") or k == "Hardware" else \
                            "GPU" if k.lower().startswith("hardware") or k == "Hardware" else "Item"
                    print(f"{prefix}  {k}:")
                    for i, item in enumerate(v, 1):
                        print(f"{prefix}    {label} {i}:")
                        for key, value in item.items():
                            print(f"{prefix}      {key}: {value}")
                else:
                    print(f"{prefix}  {k}: {', '.join(str(item) for item in v) if v else 'None'}")
            elif isinstance(v, dict):
                print_section(k, v, indent + 1)
            else:
                print(f"{prefix}  {k}: {v}")
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        print(f"{prefix}  Items:")
        for i, item in enumerate(data, 1):
            print(f"{prefix}    Item {i}:")
            for key, value in item.items():
                print(f"{prefix}      {key}: {value}")
    else:
        print(f"{prefix}  {data}")

def main():
    parser = argparse.ArgumentParser(description="Show system info.")
    parser.add_argument('--disk-partitions', action='store_true', help='Show disk partition info')
    args = parser.parse_args()

    print("=== CPU Information ===")
    cpu_info = cpu.get_cpu_info()
    
    for section_name, section_data in cpu_info.items():
        print_section(section_name, section_data)
        print()  
    
    print("=== Memory Information ===")
    memory_info = memory.get_memory_info()
    
    for section_name, section_data in memory_info.items():
        print_section(section_name, section_data)
        print()
    
    print("=== Disk Information ===")
    disk_info = disk.get_disk_info(include_partitions=args.disk_partitions)
    for section_name, section_data in disk_info.items():
        print_section(section_name, section_data)
        print()
    
    print("=== GPU Information ===")
    gpu_info = gpu.get_gpu_info()
    
    for section_name, section_data in gpu_info.items():
        print_section(section_name, section_data)
        print()
    
    print("=== Motherboard Information ===")
    motherboard_info = motherboard.get_motherboard_info()
    
    for section_name, section_data in motherboard_info.items():
        print_section(section_name, section_data)
        print()

if __name__ == "__main__":
    main()