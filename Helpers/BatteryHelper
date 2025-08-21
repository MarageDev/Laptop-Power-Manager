from PowerShellHelper import run_powershell_command as run_pwsh_cmd


"""BatteryStatus information for Windows.
Other (1) The battery is discharging.
Unknown (2) The system has access to AC so no battery is being discharged. However, the battery is not necessarily charging.
Fully Charged (3)
Low (4)
Critical (5)
Charging (6)
Charging and High (7)
Charging and Low (8)
Charging and Critical (9)
Undefined (10)
Partially Charged (11)
"""
def get_battery_status():
    command = "(Get-WmiObject win32_battery).BatteryStatus"
    status = run_pwsh_cmd(command)
    return status

def get_battery_percentage():
    command = "(Get-WmiObject win32_battery).estimatedChargeRemaining"
    percentage = run_pwsh_cmd(command)
    return int(percentage)

def get_battery_time_remaining():
    command = "(Get-WmiObject win32_battery).estimatedRunTime"
    time_remaining = run_pwsh_cmd(command)

    if time_remaining == "71582788": return -1 # Running on AC power

    return int(time_remaining)
