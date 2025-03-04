import os

def PowerCenter(data):
    try:
        command = data["command"]

        if command not in ["restart", "shutdown", "lock"]:
            return
        
        if command == "restart":
            os.system("shutdown /r /t 0")
        elif command == "shutdown":
            os.system("shutdown /s /t 0")
        elif command == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")

    except Exception as e:
        pass
