import argparse
import sys
from pathlib import Path

# Add the ui module to the path
sys.path.append(str(Path(__file__).parent / "ui"))

from system_info import cpu, memory, disk, motherboard, gpu, network, os_info, usb
from ui.cli import (
    console, print_header, print_section_header, print_section, 
    print_summary_stats, print_progress_bar, print_footer, 
    print_error, print_success, clear_screen
)

def get_system_summary():
    """Get a quick summary of system stats"""
    try:
        # Get basic info for summary
        os_info_data = os_info.get_os_info()
        cpu_info_data = cpu.get_cpu_info()
        memory_info_data = memory.get_memory_info()
        
        summary = {}
        
        # OS info
        if "System" in os_info_data and "OS" in os_info_data["System"]:
            summary["Operating System"] = os_info_data["System"]["OS"]
        
        # CPU info
        if "Basic Info" in cpu_info_data and "Model" in cpu_info_data["Basic Info"]:
            cpu_model = cpu_info_data["Basic Info"]["Model"]
            if cpu_model and len(cpu_model) > 30:
                cpu_model = cpu_model[:30] + "..."
            summary["Processor"] = cpu_model
        
        # Memory info
        if "Usage" in memory_info_data and "Total" in memory_info_data["Usage"]:
            summary["Total Memory"] = memory_info_data["Usage"]["Total"]
        
        return summary
    except Exception:
        return {}

def main():
    parser = argparse.ArgumentParser(
        description="Heracross - System Information Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                           Show basic system information
    python main.py --all-details             Show all detailed information
    python main.py --disk-partitions         Include disk partition details
    python main.py --network-details         Include network interface details
    python main.py --usb-details             Include USB device details
        """
    )
    
    parser.add_argument('--disk-partitions', action='store_true', 
                        help='Show disk partition information')
    parser.add_argument('--network-details', action='store_true', 
                        help='Show detailed network interface information')
    parser.add_argument('--usb-details', action='store_true', 
                        help='Show detailed USB device information')
    parser.add_argument('--all-details', action='store_true',
                        help='Show all detailed information')
    parser.add_argument('--no-header', action='store_true',
                        help='Skip the header and summary')
    
    args = parser.parse_args()
    
    # Enable all details if --all-details is used
    if args.all_details:
        args.disk_partitions = True
        args.network_details = True
        args.usb_details = True
    
    try:
        # Clear screen and show header
        if not args.no_header:
            clear_screen()
            print_header()
            
            # Show progress bar
            print_progress_bar("Gathering system information...")
            
            # Show summary stats
            summary = get_system_summary()
            if summary:
                print_summary_stats(summary)
        
        # Operating System Information
        print_section_header("Operating System Information")
        try:
            os_information = os_info.get_os_info()
            for section_name, section_data in os_information.items():
                print_section(section_name, section_data)
        except Exception as e:
            print_error(f"Failed to get OS information: {str(e)}")

        # CPU Information
        print_section_header("CPU Information")
        try:
            cpu_info = cpu.get_cpu_info()
            for section_name, section_data in cpu_info.items():
                print_section(section_name, section_data)
        except Exception as e:
            print_error(f"Failed to get CPU information: {str(e)}")

        # Memory Information
        print_section_header("Memory Information")
        try:
            memory_info = memory.get_memory_info()
            for section_name, section_data in memory_info.items():
                print_section(section_name, section_data)
        except Exception as e:
            print_error(f"Failed to get memory information: {str(e)}")

        # Disk Information
        print_section_header("Disk Information")
        try:
            disk_info = disk.get_disk_info(include_partitions=args.disk_partitions)
            for section_name, section_data in disk_info.items():
                print_section(section_name, section_data)
        except Exception as e:
            print_error(f"Failed to get disk information: {str(e)}")

        # GPU Information
        print_section_header("GPU Information")
        try:
            gpu_info = gpu.get_gpu_info()
            for section_name, section_data in gpu_info.items():
                print_section(section_name, section_data)
        except Exception as e:
            print_error(f"Failed to get GPU information: {str(e)}")

        # Network Information
        print_section_header("Network Information")
        try:
            network_info = network.get_network_info(include_details=args.network_details)
            for section_name, section_data in network_info.items():
                print_section(section_name, section_data)
        except Exception as e:
            print_error(f"Failed to get network information: {str(e)}")

        # USB Information
        print_section_header("USB Information")
        try:
            usb_info = usb.get_usb_info(include_details=args.usb_details)
            for section_name, section_data in usb_info.items():
                print_section(section_name, section_data)
        except Exception as e:
            print_error(f"Failed to get USB information: {str(e)}")

        # Motherboard Information
        print_section_header("Motherboard Information")
        try:
            motherboard_info = motherboard.get_motherboard_info()
            for section_name, section_data in motherboard_info.items():
                print_section(section_name, section_data)
        except Exception as e:
            print_error(f"Failed to get motherboard information: {str(e)}")

        # Footer
        if not args.no_header:
            print_footer()
            print_success("System information gathering completed successfully!")

    except KeyboardInterrupt:
        print_error("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()