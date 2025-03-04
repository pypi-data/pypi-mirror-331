import subprocess
import threading
import queue

def create_shell():
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
        bufsize=1
    )

    stdout_queue = queue.Queue()
    stderr_queue = queue.Queue()

    stdout_thread = threading.Thread(target=read_output, args=(shell.stdout, stdout_queue), daemon=True)
    stderr_thread = threading.Thread(target=read_output, args=(shell.stderr, stderr_queue), daemon=True)
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()

    return shell, stdout_queue, stderr_queue


class ShellHandler:
    def __init__(self):
        self.shell = None
        self.stdout_queue = None
        self.stderr_queue = None

        self.initiate()

    def initiate(self):
        self.shell, self.stdout_queue, self.stderr_queue = create_shell()

    def get_shell(self):
        if not self.shell or not self.stdout_queue or not self.stderr_queue or self.shell.poll() is not None:
            self.initiate()
        return self.shell, self.stdout_queue, self.stderr_queue

    def close_connection(self):
        if self.shell:
            self.shell.stdin.write('exit\n')
            self.shell.stdin.write('exit\n')
            self.shell.stdin.write('exit\n')
            self.shell.stdin.flush()  
            self.shell.wait()
            self.shell = None 
            self.stdout_queue.queue.clear()
            self.stderr_queue.queue.clear()