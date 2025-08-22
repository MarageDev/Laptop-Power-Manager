import ttkbootstrap as ttk
import tkinter as tk
import pywinstyles
import sv_ttk
import PowerPlanHelper
import BatteryHelper
import threading
import queue
import time

STATUS_UPDATE_INTERVAL = 2  # seconds between background fetches

# --- Main window setup ---
root = ttk.Window(
    title="Laptop Power Manager",
    themename="darkly",
    size=(600, 400),
    resizable=(True, True)
)
root.iconphoto(False, ttk.PhotoImage(file="icon_32.png"))
root.configure(bg="#202020")

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=1)

# --- Content ---
content = ttk.Frame(root, padding=20)
content.grid(row=0, column=0, sticky="nsew")

# --- Section 1: Select Power Plan ---
plan_frame = ttk.Labelframe(content, text="Select Power Plan", padding=15, bootstyle="info")
plan_frame.pack(fill="x", pady=(0, 15))

plan_var = tk.StringVar()
power_plan_combo = ttk.Combobox(plan_frame, textvariable=plan_var, state="readonly")
power_plan_combo.pack(fill="x", pady=5)

plans = []
plan_map = {}
try:
    plans = PowerPlanHelper.get_power_plans()
    plan_names = [p["Name"] for p in plans]
    plan_map = {p["Name"]: p["GUID"] for p in plans}
    power_plan_combo["values"] = plan_names
    active_plan = next((p for p in plans if p["Active"]), None)
    if active_plan:
        plan_var.set(active_plan["Name"])
    else:
        plan_var.set(plan_names[0] if plan_names else "No Plans")
except Exception as e:
    power_plan_combo["values"] = ["Error loading plans"]
    plan_var.set("Error")
    print("Error loading power plans:", e)

def change_power_plan(event=None):
    selected_name = plan_var.get()
    selected_guid = plan_map.get(selected_name)
    if not selected_guid:
        print(f"Could not find GUID for plan: {selected_name}")
        return
    try:
        PowerPlanHelper.set_active_power_plan(selected_guid)
        print(f"Changed power plan to: {selected_name} ({selected_guid})")
    except Exception as e:
        print("Failed to change power plan:", e)

power_plan_combo.bind("<<ComboboxSelected>>", change_power_plan)

# --- Section 2: Open Power Plans ---
open_frame = ttk.Labelframe(content, text="Manually Edit Power Plans", padding=15, bootstyle="secondary")
open_frame.pack(fill="x", pady=(0, 5))

open_button = ttk.Button(open_frame, text="Open Power Options", bootstyle="primary", command=PowerPlanHelper.open_power_options_control_panel)
open_button.pack(fill="x", pady=5)

# --- Separator above status bar ---
separator_top = ttk.Separator(root, orient="horizontal")
separator_top.grid(row=1, column=0, sticky="ew")

# --- Status bar (brightened) ---
status_bar = tk.Frame(root, bg="#f8f8f8", height=25)  # use tk.Frame to force bg
status_bar.grid(row=2, column=0, sticky="ew")

power_plan_label = tk.Label(status_bar, text="Power Plan: Loading...", bg="#f8f8f8", fg="black")
battery_label = tk.Label(status_bar, text="Battery: Loading...", bg="#f8f8f8", fg="black")
time_label = tk.Label(status_bar, text="Time Remaining: Loading...", bg="#f8f8f8", fg="black")

power_plan_label.pack(side="left", padx=12, pady=2)
time_label.pack(side="right", padx=(6, 12), pady=2)
separator = ttk.Separator(status_bar, orient="vertical")
separator.pack(side="right", fill="y", pady=2)
battery_label.pack(side="right", padx=(12, 6), pady=2)

# --- Thread-safe queue for status data ---
status_queue = queue.Queue(maxsize=1)  # maxsize=1 ensures only latest data kept

# --- Background thread fetching status ---
def status_fetcher():
    while True:
        try:
            plan = PowerPlanHelper.get_active_power_plan()
            battery = BatteryHelper.get_battery_percentage()
            time_remaining = BatteryHelper.get_battery_time_remaining()

            if not time_remaining or time_remaining == -1:
                time_str = "Unknown"
            else:
                hours = int(time_remaining) // 60
                minutes = int(time_remaining) % 60
                time_str = f"{hours}h {minutes}m" if hours else f"{minutes}m"

            if status_queue.full():
                try:
                    status_queue.get_nowait()
                except queue.Empty:
                    pass
            status_queue.put_nowait((plan, battery, time_str))
        except Exception as e:
            if status_queue.full():
                try:
                    status_queue.get_nowait()
                except queue.Empty:
                    pass
            status_queue.put_nowait(("Error", "?", "?"))
            print("Background status fetch error:", e)

        time.sleep(STATUS_UPDATE_INTERVAL)

# --- Main thread polling function to update UI ---
def poll_status_queue():
    try:
        plan, battery, time_str = status_queue.get_nowait()
        power_plan_label.config(text=f"Power Plan: {plan}")
        battery_label.config(text=f"Battery: {battery}%")
        time_label.config(text=f"Time Remaining: {time_str}")
    except queue.Empty:
        pass
    finally:
        root.after(200, poll_status_queue)

# Start background thread
threading.Thread(target=status_fetcher, daemon=True).start()
# Start polling UI update
root.after(200, poll_status_queue)

# --- Styling ---
sv_ttk.use_dark_theme()
pywinstyles.change_header_color(root, "#1c1c1c")

# --- Start main loop ---
root.mainloop()
