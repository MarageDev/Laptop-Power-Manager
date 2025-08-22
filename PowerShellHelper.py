import subprocess

def run_powershell_command(command):
    
    # Executes a PowerShell command and returns 
    # the output as seen on the PowerShell window.

    result = subprocess.run(
        ["powershell", "-Command", command],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"PowerShell command failed: {result.stderr}")
    return result.stdout.strip()

