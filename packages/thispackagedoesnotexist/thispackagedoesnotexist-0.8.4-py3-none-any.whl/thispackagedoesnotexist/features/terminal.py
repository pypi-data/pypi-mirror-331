import time
import traceback

def terminal(self, data):
    try:
        
        shell, stdout_queue, stderr_queue = self.shell_handler.get_shell()
        command = data["terminal"]
        
        shell.stdin.write(command + "\n")
        shell.stdin.flush()

        time.sleep(0.5)
        output = ""

        while not stdout_queue.empty() or not stderr_queue.empty():
            while not stdout_queue.empty():
                output += stdout_queue.get_nowait()
            while not stderr_queue.empty():
                output += stderr_queue.get_nowait()
        
        if command == "CLOSE":
            self.shell_handler.close_connection()
            output = "Connection closed. You can send a command to initiate it again or close the window"

        response = output.replace("Not enough memory resources are available to process this command.", "") if output else "Command executed successfully.\n"
        
        self.send_message('response', self.converter.encode({"terminal": response}))

    except Exception as e:
        self.send_message('response', self.converter.encode({"terminal_logger": f"From Client: {traceback.format_exc()}"}))
