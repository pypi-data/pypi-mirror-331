import platform
import http.client
from wmi import WMI
import winreg
import ctypes
import json
import ssl
import pythoncom
import subprocess
import sys


class ClientInfo:
    def __init__(self):
        self.ip = None
        self.country = None
        self.pc_name = platform.node()
        self.pc_id = WMI().Win32_ComputerSystemProduct()[0].UUID
        self.os = self.get_win_ver()
        self.account_type = self.check_account_type()
        self.fetch_client_info()
        self.version = self.get_installed_version()
        pythoncom.CoInitialize()

    def get_win_ver(self):
        system_info = platform.system()
        architecture = platform.architecture()[0]
        if system_info == "Windows":
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                    edition = winreg.QueryValueEx(key, "ProductName")[0]
                    version = winreg.QueryValueEx(key, "ReleaseId")[0]
                return f"{edition} {version} {architecture}"
            except Exception:
                return "Error retrieving Windows edition"
        return "Not a Windows system"

    def check_account_type(self):
        try:
            return "Admin" if ctypes.windll.shell32.IsUserAnAdmin() != 0 else "User"
        except Exception:
            return "None"

    def fetch_client_info(self):
        try:
            url = "api.country.is"
            context = ssl._create_unverified_context()
            conn = http.client.HTTPSConnection(url, context=context)
            conn.request("GET", "/")
            response = conn.getresponse()
            
            if response.status == 200:
                data = json.loads(response.read().decode())
                self.ip = data.get("ip")
                self.country = data.get("country")
            
            conn.close()
        except Exception:
            self.ip = None
            self.country = None

    def get_installed_version(self):
        try:
            output = subprocess.run(
                [sys.executable, "-m", "pip", "show", "thispackagedoesnotexist"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            ).stdout
            for line in output.splitlines():
                if line.startswith("Version: "):
                    return line.split("Version: ")[1].strip()
        except Exception:
            pass
        return None

    def get_details(self):
        return {
            "IP": self.ip,
            "PC Name": self.pc_name,
            "PC ID": self.pc_id,
            "OS": self.os,
            "Account Type": self.account_type,
            "Country": self.country,
            "Version": self.version,
        }