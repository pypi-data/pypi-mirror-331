from ..plugins.client import ClientControl
import time

def ClientCenter(data):
    try:
        command = data["command"]

        if command not in ["restart", "shutdown", "update", "uninstall"]:
            return
        
        if command == "restart":
            ClientControl.restart_self()
        elif command == "shutdown":
            ClientControl.shutdown_self()
        elif command == "update":
            ClientControl.restart_self()
        elif command == "uninstall":
            ClientControl.uninstall_self()

    except Exception as e:
        pass
