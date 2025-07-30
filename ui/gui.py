import tkinter as tk
from tkinter import ttk
from system_info import cpu, memory, disk, motherboard, gpu, network, usb, os_info
from PIL import Image, ImageTk

class HardwareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HERACROSS - System Information")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a237e")  

        try:
            self.root.iconphoto(True, tk.PhotoImage(file="ui/heracross.png"))
        except Exception:
            pass 

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#283593", borderwidth=2, relief="raised")
        style.configure("TNotebook.Tab", 
                        font=("Segoe UI", 11, "bold"), 
                        padding=[15, 8],
                        background="#3949ab",
                        foreground="#ffffff")
        style.map("TNotebook.Tab", 
                    background=[("selected", "#ffc107"),  
                            ("active", "#5c6bc0")],    
                    foreground=[("selected", "#1a237e")])  
        
        style.configure("TFrame", background="#283593")
        style.configure("TLabel", background="#283593", foreground="#ffffff")
        style.configure("Header.TLabel", 
                        font=("Segoe UI", 20, "bold"), 
                        background="#283593",  
                        foreground="#ffc107")  
        style.configure("Section.TLabel", 
                        font=("Segoe UI", 12, "bold"), 
                        foreground="#ffc107",
                        background="#283593") 
        style.configure("TButton",
                        font=("Segoe UI", 10, "bold"),
                        background="#ffc107",
                        foreground="#1a237e")
        style.map("TButton",
                    background=[("active", "#ffca28")])

        header = ttk.Frame(root, style="TFrame")
        header.pack(fill="x", padx=15, pady=(15, 0))

        try:
            img = Image.open("ui/heracross.png")
            img = img.resize((64, 64), Image.NEAREST) 
            self.heracross_img = ImageTk.PhotoImage(img)
            img_label = ttk.Label(header, image=self.heracross_img, style="TLabel")
            img_label.pack(side="left", padx=(0, 15))
        except Exception:
            pass

        title_frame = ttk.Frame(header, style="TFrame")
        title_frame.pack(side="left", expand=True, fill="x")
        
        ttk.Label(title_frame, text="⚡ HERACROSS ⚡", style="Header.TLabel").pack(anchor="w")
        subtitle_label = ttk.Label(title_frame, 
                                    text="Sistema de Informações de Hardware", 
                                    font=("Segoe UI", 11, "italic"),
                                    background="#283593",   
                                    foreground="#b39ddb")  
        subtitle_label.pack(anchor="w", pady=(2, 0))

        ttk.Button(header, text="🔄 Update", command=self.refresh).pack(side="right", padx=(10, 0))

        self.loading_overlay = None

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=1, fill="both", padx=15, pady=15)

        self.create_tab("🧠 CPU", cpu.get_cpu_info())
        self.create_tab("🧮 Memory", memory.get_memory_info())
        self.create_tab("💾 Disk", disk.get_disk_info())
        self.create_tab("🔧 Motherboard", motherboard.get_motherboard_info())
        self.create_tab("⚙️ BIOS", motherboard.get_bios_info())
        self.create_tab("🎮 GPU", gpu.get_gpu_info())
        self.create_tab("🌐 Network", network.get_network_info())
        self.create_tab_list("🔌 USB", usb.get_usb_devices_info())
        self.create_tab("💻 System", os_info.get_os_info())

    def show_loading(self):
        if self.loading_overlay is None:
            self.loading_overlay = tk.Toplevel(self.root)
            self.loading_overlay.title("")
            self.loading_overlay.geometry("300x150")
            self.loading_overlay.configure(bg="#283593")
            self.loading_overlay.resizable(False, False)
            self.loading_overlay.transient(self.root)
            self.loading_overlay.grab_set()
            
            self.loading_overlay.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
            self.loading_overlay.geometry(f"300x150+{x}+{y}")
            
            loading_frame = tk.Frame(self.loading_overlay, bg="#283593")
            loading_frame.pack(expand=True, fill="both")
            
            title_label = tk.Label(loading_frame, 
                                    text="⚡ HERACROSS ⚡",
                                    font=("Segoe UI", 14, "bold"),
                                    bg="#283593",
                                    fg="#ffc107")
            title_label.pack(pady=(20, 10))
            
            self.loading_label = tk.Label(loading_frame,
                                        text="🔄 Updating...",
                                        font=("Segoe UI", 11),
                                        bg="#283593",
                                        fg="#ffffff")
            self.loading_label.pack(pady=5)
            
            self.progress_var = tk.StringVar()
            self.progress_label = tk.Label(loading_frame,
                                            textvariable=self.progress_var,
                                            font=("Segoe UI", 10),
                                            bg="#283593",
                                            fg="#b39ddb")
            self.progress_label.pack(pady=(10, 20))
            
            self.animate_loading()

    def animate_loading(self):
        if self.loading_overlay and self.loading_overlay.winfo_exists():
            dots = ["", ".", "..", "..."]
            current_text = self.progress_var.get()
            
            if current_text == "":
                next_text = "."
            elif current_text == ".":
                next_text = ".."
            elif current_text == "..":
                next_text = "..."
            else:
                next_text = ""
                
            self.progress_var.set(next_text)
            
            self.root.after(500, self.animate_loading)

    def hide_loading(self):
        if self.loading_overlay:
            self.loading_overlay.destroy()
            self.loading_overlay = None

    def refresh(self):
        self.show_loading()
        
        self.root.after(100, self.do_refresh)

    def do_refresh(self):
        try:
            for tab in self.tabs.tabs():
                self.tabs.forget(tab)
            
            self.create_tab("🧠 CPU", cpu.get_cpu_info())
            self.create_tab("🧮 Memory", memory.get_memory_info())
            self.create_tab("💾 Disk", disk.get_disk_info())
            self.create_tab("🔧 Motherboard", motherboard.get_motherboard_info())
            self.create_tab("⚙️ BIOS", motherboard.get_bios_info())
            self.create_tab("🎮 GPU", gpu.get_gpu_info())
            self.create_tab("🌐 Network", network.get_network_info())
            self.create_tab_list("🔌 USB", usb.get_usb_devices_info())
            self.create_tab("💻 System", os_info.get_os_info())

        finally:
            self.root.after(500, self.hide_loading)

    def create_tab(self, title, data):
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text=title)
        canvas = tk.Canvas(frame, bg="#283593", highlightthickness=0) 
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.configure(style="TFrame")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        scroll_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(scroll_frame, text=title, style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(15, 10))
        row = 1

        def render_value(key, value, row, indent=0):
            pad = 25 + indent * 25
            if isinstance(value, dict):
                key_label = ttk.Label(scroll_frame, text=f"{key}:", 
                                    font=("Segoe UI", 10, "bold"),
                                    background="#283593",
                                    foreground="#e8eaf6")
                key_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=pad, pady=3)
                row += 1
                for subkey, subval in value.items():
                    row = render_value(subkey, subval, row, indent + 1)
            elif isinstance(value, list):
                key_label = ttk.Label(scroll_frame, text=f"{key}:", 
                                    font=("Segoe UI", 10, "bold"),
                                    background="#283593",
                                    foreground="#e8eaf6")
                key_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=pad, pady=3)
                row += 1
                for idx, item in enumerate(value):
                    row = render_value(f"{key} {idx+1}", item, row, indent + 1)
            else:
                key_label = ttk.Label(scroll_frame, text=f"{key}:", 
                                    font=("Segoe UI", 10, "bold"),
                                    background="#283593",
                                    foreground="#e8eaf6")
                key_label.grid(row=row, column=0, sticky="nw", padx=pad, pady=3)
                
                value_label = ttk.Label(scroll_frame, text=str(value), 
                                        font=("Segoe UI", 10),
                                        background="#283593",
                                        foreground="#ffffff")
                value_label.grid(row=row, column=1, sticky="nw", padx=15, pady=3)
                row += 1
            return row

        for key, value in data.items():
            row = render_value(key, value, row)

    def create_tab_list(self, title, items):
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text=title)
        canvas = tk.Canvas(frame, bg="#283593", highlightthickness=0)  # Mesma cor do frame
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.configure(style="TFrame")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        scroll_frame.grid_columnconfigure(1, weight=1)

        def render_item(key, value, row, indent=0):
            pad = 25 + indent * 25
            if isinstance(value, dict):
                if not value:
                    empty_label = ttk.Label(scroll_frame, text="Nenhuma informação disponível", 
                                            font=("Segoe UI", 10, "italic"),
                                            background="#283593",
                                            foreground="#b39ddb")
                    empty_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=pad, pady=3)
                    row += 1
                else:
                    if key: 
                        key_label = ttk.Label(scroll_frame, text=f"{key}:", 
                                            font=("Segoe UI", 10, "bold"),
                                            background="#283593",
                                            foreground="#e8eaf6")
                        key_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=pad, pady=3)
                        row += 1
                    for subkey, subval in value.items():
                        row = render_item(subkey, subval, row, indent + 1)
            elif isinstance(value, list):
                if not value:
                    empty_label = ttk.Label(scroll_frame, text="Nenhuma informação disponível", 
                                            font=("Segoe UI", 10, "italic"),
                                            background="#283593",
                                            foreground="#b39ddb")
                    empty_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=pad, pady=3)
                    row += 1
                else:
                    if key:  
                        key_label = ttk.Label(scroll_frame, text=f"{key}:", 
                                            font=("Segoe UI", 10, "bold"),
                                            background="#283593",
                                            foreground="#e8eaf6")
                        key_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=pad, pady=3)
                        row += 1
                    for idx, item in enumerate(value):
                        row = render_item(f"{key} {idx+1}" if key else f"Item {idx+1}", item, row, indent + 1)
            else:
                if key:  
                    key_label = ttk.Label(scroll_frame, text=f"{key}:", 
                                        font=("Segoe UI", 10, "bold"),
                                        background="#283593",
                                        foreground="#e8eaf6")
                    key_label.grid(row=row, column=0, sticky="nw", padx=pad, pady=3)
                    
                    value_label = ttk.Label(scroll_frame, text=str(value), 
                                            font=("Segoe UI", 10),
                                            background="#283593",
                                            foreground="#ffffff")
                    value_label.grid(row=row, column=1, sticky="nw", padx=15, pady=3)
                else:
                    value_label = ttk.Label(scroll_frame, text=str(value), 
                                            font=("Segoe UI", 10),
                                            background="#283593",
                                            foreground="#ffffff")
                    value_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=pad, pady=3)
                row += 1
            return row

        row = 0
        if not items:
            empty_label = ttk.Label(scroll_frame, text="Nenhuma informação disponível", 
                                    font=("Segoe UI", 10, "italic"),
                                    background="#283593",
                                    foreground="#b39ddb")
            empty_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=25, pady=15)
            row += 1
        else:
            for i, item in enumerate(items):
                section_label = ttk.Label(scroll_frame, text=f"⚡ {title} {i+1}", style="Section.TLabel")
                section_label.grid(row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=(15, 5))
                row += 1
                
                row = render_item("", item, row)
                
                
                separator_frame = tk.Frame(scroll_frame, height=2, bg="#ffc107")
                separator_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=25, pady=10)
                row += 1

