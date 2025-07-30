from system_info import cpu

def main():
    cpu_info = cpu.get_cpu_info()
    print("CPU Info:")
    for k, v in cpu_info.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()