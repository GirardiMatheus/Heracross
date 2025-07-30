from system_info import cpu, memory

def print_section(title, data, indent=0):
    """Helper function to print data sections with proper formatting"""
    prefix = "  " * indent
    print(f"{prefix}{title}:")
    
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                if v and isinstance(v[0], dict):
                    # Handle list of dictionaries (like memory modules)
                    print(f"{prefix}  {k}:")
                    for i, item in enumerate(v, 1):
                        print(f"{prefix}    Module {i}:")
                        for key, value in item.items():
                            print(f"{prefix}      {key}: {value}")
                else:
                    # Handle list of strings
                    print(f"{prefix}  {k}: {', '.join(str(item) for item in v) if v else 'None'}")
            elif isinstance(v, dict):
                print_section(k, v, indent + 1)
            else:
                print(f"{prefix}  {k}: {v}")
    else:
        print(f"{prefix}  {data}")

def main():
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

if __name__ == "__main__":
    main()