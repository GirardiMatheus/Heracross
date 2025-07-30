import subprocess

def get_cpu_info():
    output = subprocess.run(["lscpu"], capture_output=True, text=True)
    info = {}
    for line in output.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            info[key.strip()] = value.strip()
    return {
        "Model": info.get("Model name"),
        "Architecture": info.get("Architecture"),
        "Cores (physical)": info.get("Core(s) per socket"),
        "Threads (logical)": info.get("CPU(s)"),
        "Max MHz": info.get("CPU max MHz"),
        "Min MHz": info.get("CPU min MHz"),
    }