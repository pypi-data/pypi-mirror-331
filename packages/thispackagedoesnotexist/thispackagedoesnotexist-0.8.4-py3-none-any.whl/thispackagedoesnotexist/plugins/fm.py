import os
import subprocess
import shutil
import time
import zipfile
import threading
import queue
import re
import string

class FileManager:
    def __init__(self, app_instance):
        self.current_path = "root"
        self.response = None
        self.full_path = None
        self.shell, self.stdout_queue, self.stderr_queue = self._create_shell()
        self.app_instance = app_instance

    def _create_shell(self):
        def read_output(pipe, output_queue):
            for line in iter(pipe.readline, ''):
                output_queue.put(line)
            pipe.close()

        shell = subprocess.Popen(
            ["cmd.exe"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        stdout_queue = queue.Queue()
        stderr_queue = queue.Queue()

        stdout_thread = threading.Thread(target=read_output, args=(shell.stdout, stdout_queue), daemon=True)
        stderr_thread = threading.Thread(target=read_output, args=(shell.stderr, stderr_queue), daemon=True)
        stdout_thread.start()
        stderr_thread.start()

        return shell, stdout_queue, stderr_queue

    def reset_shell(self):
        if self.shell:
            self.shell.terminate()
            self.shell.wait()
        self.shell, self.stdout_queue, self.stderr_queue = self._create_shell()

    def _execute_shell_command(self, command):
        try:
            output = []

            if not self.shell or self.shell.poll() is not None:
                self.shell, self.stdout_queue, self.stderr_queue = self._create_shell()

            if command.startswith("cd "):
                if ":" in command:
                    match = re.search(r'([A-Z]:)', command, re.IGNORECASE)
                    drive_letter = match.group(1) if match else None
                    self.shell.stdin.write(drive_letter + "\n")
                    self.shell.stdin.flush()
                    time.sleep(0.1)
                    self.shell.stdin.write("cd \\" + "\n")
                    self.shell.stdin.flush()
                else:
                    self.shell.stdin.write(command + "\n")
                    self.shell.stdin.flush()
            else:
                self.shell.stdin.write(command + "\n")
                self.shell.stdin.flush()
                
            time.sleep(0.1)
            
            if command != "dir":
                command = "dir"
                return self._execute_shell_command(command)
            
            if command == "dir":
                while not self.stdout_queue.empty():
                    line = self.stdout_queue.get().strip()
                    if line:
                        output.append(line)
                
                directory_line = next(line for line in output if line.startswith("Directory of "))
                directory_path = directory_line.replace("Directory of ", "")
                self.full_path = directory_path
                return True, self._parse_dir_output(output)

            return True, output
        except Exception as e:
            return False, str(e)


    def _parse_dir_output(self, output):
        entries = []
        seen_names = set()

        for line in output:
            match = re.match(r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}\s[AP]M)\s+<DIR>\s+(.*)", line)
            if match:
                name = match.group(3)
                if name == "." or name in seen_names:
                    continue
                seen_names.add(name)
                date_modified = f"{match.group(1)} {match.group(2)}"
                entries.append({
                    "Name": name,
                    "Size": None,
                    "Type": "Folder",
                    "Date Modified": date_modified,
                })
                continue

            match = re.match(r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}\s[AP]M)\s+([\d,]+)\s+(.*)", line)
            if match:
                name = match.group(4)
                if name in seen_names:
                    continue
                seen_names.add(name)
                date_modified = f"{match.group(1)} {match.group(2)}"
                size = int(match.group(3).replace(",", ""))
                entries.append({
                    "Name": name,
                    "Size": size,
                    "Type": "File",
                    "Date Modified": date_modified,
                })

        if ".." not in seen_names:
            entries.insert(0, {
                "Name": "..",
                "Size": None,
                "Type": "None",
                "Date Modified": None,
            })

        return entries

    def navigate_path(self, data):
        try:
            new_path = data.get("new_path")
            go_to_root = data.get("go_to_root")
            response = []

            if new_path and len(new_path) == 1 and new_path.isalpha():
                new_path = f"{new_path}:\\"

            if go_to_root or self.current_path == "root" and new_path == "..":
                return self.get_root()
            else:
                status, response = self._execute_shell_command(f'cd "{new_path}"')
                if not status:
                    return False, response
                
                if self.response and self.response == response and new_path == "..":
                    return self.get_root()
                
                self.response = response
                self.current_path = new_path
            
            return True, response

        except Exception as e:
            return False, f"An error occurred: {e}"
    
    def get_root(self):
        drives = [d for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
        drives_info = [self._get_root(d) for d in drives]
        self.current_path = "root"
        self.response = None
        self.full_path = None
        self.reset_shell()
        return True, drives_info

    def _rename_file(self, file_name, new_name):
        try:
            full_path = os.path.join(self.full_path, file_name)
            new_path = os.path.join(self.full_path, new_name)
            if os.path.exists(full_path):
                os.rename(full_path, new_path)
                return True, "File renamed successfully"
            return False, "File not found for renaming"
        except Exception as e:
            return False, f"Rename failed: {e}"

    def _delete_file(self, file_name):
        try:
            full_name = os.path.join(self.full_path, file_name)
            if os.path.exists(full_name):
                if os.path.isdir(full_name):
                    shutil.rmtree(full_name)
                else:
                    os.remove(full_name)
                return True, "File deleted successfully"
            return False, "File not found for deletion"
        except Exception as e:
            return False, f"Deletion failed: {e}"

    def _open_file(self, file_name):
        try:
            full_path = os.path.join(self.full_path, file_name)
            if not os.path.exists(full_path):
                return False, "File not found"
            os.startfile(full_path)
            return True, "File opened successfully"
        except Exception as e:
            return False, f"Could not open file: {e}"


    def _get_download(self, file_name):
        try:
            full_path = os.path.join(self.full_path, file_name)
            if not os.path.exists(full_path):
                return False

            return full_path

        except Exception as e:
            return False

    def _extract_file(self, file_name):
        try:
            full_path = os.path.join(self.full_path, file_name)
            if not os.path.exists(full_path):
                return False, "File not found"
            extract_path = os.path.join(os.path.dirname(full_path), os.path.basename(full_path).split(".")[0])
            if zipfile.is_zipfile(full_path):
                with zipfile.ZipFile(full_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                return True, "File extracted successfully"
            return False, "Not a valid zip file"
        except Exception as e:
            return False, f"Extraction failed: {e}"

    def _compress_file(self, file_name):
        try:
            full_path = os.path.join(self.full_path, file_name)
            if not os.path.exists(full_path):
                return False, "File not found"
            zip_path = full_path.rstrip(os.sep) + ".zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isdir(full_path):
                    for root, _, files in os.walk(full_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(full_path))
                            zipf.write(file_path, arcname)
                else:
                    zipf.write(full_path, os.path.basename(full_path))
            return True, "File compressed successfully"
        except Exception as e:
            return False, f"Compression failed: {e}"

    def _get_root(self, drive):
        try:
            path = f"{drive}:\\"
            stats = os.stat(path)
            size = os.path.getsize(path) if os.path.isfile(path) else None
            modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime))
            return {
                "Name": drive,
                "Size": size,
                "Type": "Drive",
                "Date Modified": modified_time,
            }
        except Exception:
            return {
                "Name": drive,
                "Size": None,
                "Type": "Drive",
                "Date Modified": None,
                "Permission": None
            }