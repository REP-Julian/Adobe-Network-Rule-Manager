import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    params = " ".join(['"{}"'.format(arg) for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def browse_path():
    filepath = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")])
    if filepath:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, os.path.normpath(filepath))

def apply_rules():
    target_path = dir_entry.get()
    block_in = inbound_var.get()
    block_out = outbound_var.get()

    if not block_in and not block_out:
        messagebox.showerror("Error", "Please select a network rule to disable.")
        return

    selected_indices = adobe_list.curselection()
    if not selected_indices:
        app_name = "Adobe Product"
    else:
        app_name = adobe_list.get(selected_indices[0])
        
        if app_name == "Adobe Acrobat Pro":
            if "adobe" not in target_path.lower() and "acrobat" not in target_path.lower():
                messagebox.showerror("Error", "The selected path does not match the chosen product.")
                return
        else:
            product_keyword = app_name.replace("Adobe ", "").lower()
            if product_keyword not in target_path.lower():
                messagebox.showerror("Error", "The selected path does not match the chosen product.")
                return

    exe_files = []
    target_path = os.path.normpath(target_path)
    
    if os.path.isfile(target_path) and target_path.lower().endswith(".exe"):
        exe_files.append(target_path)
    elif os.path.isdir(target_path):
        for root_dir, _, files in os.walk(target_path):
            for file in files:
                if file.lower().endswith(".exe"):
                    exe_files.append(os.path.join(root_dir, file))
    else:
        messagebox.showerror("Error", "Please select a valid file or directory.")
        return

    if not exe_files:
        messagebox.showinfo("Info", "No executable files found in the directory.")
        return

    error_count = 0
    error_message = ""
    netsh_path = r"C:\Windows\System32\netsh.exe"

    for exe in exe_files:
        exe_clean = os.path.normpath(exe)
        rule_name = f"Block {app_name} - {os.path.basename(exe_clean)}"

        if block_in:
            cmd_in = f'{netsh_path} advfirewall firewall add rule name="{rule_name} In" dir=in action=block program="{exe_clean}" enable=yes'
            try:
                subprocess.run(cmd_in, shell=True, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                error_count += 1
                if not error_message:
                    error_message = e.stderr.strip() or e.stdout.strip()

        if block_out:
            cmd_out = f'{netsh_path} advfirewall firewall add rule name="{rule_name} Out" dir=out action=block program="{exe_clean}" enable=yes'
            try:
                subprocess.run(cmd_out, shell=True, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                error_count += 1
                if not error_message:
                    error_message = e.stderr.strip() or e.stdout.strip()

    if error_count > 0:
        messagebox.showerror("Error", f"Failed to process {error_count} rules.\n\nDetails: {error_message}")
    else:
        messagebox.showinfo("Complete", f"Processed rules for {len(exe_files)} executable files.")
        
    subprocess.Popen("wf.msc", shell=True)

root = tk.Tk()
root.title("Task Manager")
icon_path = resource_path("Adobe.ico")
try:
    root.iconbitmap(icon_path)
except Exception:
    pass
root.geometry("1280x720")
root.state('normal')
root.resizable(True, True)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

left_frame = tk.Frame(root, borderwidth=2, relief="groove")
left_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

tk.Label(left_frame, text="Adobe Products", font=("Arial", 14)).pack(pady=10)
adobe_list = tk.Listbox(left_frame, font=("Arial", 12))
adobe_list.pack(fill="both", expand=True, padx=10, pady=10)

products = [
    "Adobe Photoshop",
    "Adobe Illustrator",
    "Adobe InDesign",
    "Adobe Premiere Pro",
    "Adobe After Effects",
    "Adobe Lightroom",
    "Adobe Lightroom Classic",
    "Adobe Acrobat Pro",
    "Adobe Audition",
    "Adobe Animate",
    "Adobe Dreamweaver",
    "Adobe InCopy",
    "Adobe Character Animator",
    "Adobe Media Encoder",
    "Adobe Bridge",
    "Adobe Express",
    "Adobe Fresco",
    "Adobe Firefly",
    "Adobe XD",
    "Adobe Dimension",
    "Adobe Aero"
]

for item in products:
    adobe_list.insert(tk.END, item)

top_right_frame = tk.Frame(root, borderwidth=2, relief="groove")
top_right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

tk.Label(top_right_frame, text="Application Path", font=("Arial", 14)).pack(pady=10)
dir_frame = tk.Frame(top_right_frame)
dir_frame.pack(pady=20, fill="x", padx=20)

dir_entry = tk.Entry(dir_frame, font=("Arial", 12))
dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

browse_btn = tk.Button(dir_frame, text="Browse", font=("Arial", 12), command=browse_path)
browse_btn.pack(side="right")

bottom_right_frame = tk.Frame(root, borderwidth=2, relief="groove")
bottom_right_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

tk.Label(bottom_right_frame, text="Network Rules", font=("Arial", 14)).pack(pady=10)

inbound_var = tk.BooleanVar()
outbound_var = tk.BooleanVar()

inbound_check = tk.Checkbutton(bottom_right_frame, text="Disable Inbound Network", variable=inbound_var, font=("Arial", 12))
inbound_check.pack(anchor="w", padx=20, pady=5)

outbound_check = tk.Checkbutton(bottom_right_frame, text="Disable Outbound Network", variable=outbound_var, font=("Arial", 12))
outbound_check.pack(anchor="w", padx=20, pady=5)

button_frame = tk.Frame(bottom_right_frame)
button_frame.pack(side="bottom", fill="x", pady=20, padx=20)

credits_label = tk.Label(button_frame, text="Credits: Julian", font=("Arial", 10), fg="gray")
credits_label.pack(side="left", padx=5)

start_btn = tk.Button(button_frame, text="Start", font=("Arial", 12), width=10, command=apply_rules)
start_btn.pack(side="right", padx=5)

cancel_btn = tk.Button(button_frame, text="Cancel", font=("Arial", 12), width=10, command=root.destroy)
cancel_btn.pack(side="right", padx=5)

root.mainloop()