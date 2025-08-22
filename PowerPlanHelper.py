from PowerShellHelper import run_powershell_command as run_pwsh_cmd
import re

def get_power_plans():
    command = "powercfg -LIST"
    power_plans = run_pwsh_cmd(command)
    
    # Regex to capture the GUID, name, and active status of each power plan
    pattern = re.compile(r"([0-9a-fA-F-]{36})\s*\((.*?)\)\s*(\*?)")
    
    plans = []
    for match in pattern.finditer(power_plans):
        guid, name, active = match.groups()
        plans.append({
            "GUID": guid,
            "Name": name,
            "Active": bool(active.strip())
        })
    return plans 

def set_active_power_plan(guid):
    command = f"powercfg -SETACTIVE {guid}"
    run_pwsh_cmd(command)

    # Verify if the plan was set successfully
    if get_active_power_plan() == guid:
        return True
    return False

def get_active_power_plan():
    command = "powercfg -GETACTIVESCHEME"
    active_plan = run_pwsh_cmd(command)
    
    # Extract the GUID from the output
    match = re.search(r"\((.*?)\)", active_plan)
    if match:
        return match.group(1).strip()
    return None

def open_power_options_control_panel():
    command = "control powercfg.cpl"
    run_pwsh_cmd(command)
