from PIL import Image
import mss
import io
import base64
import traceback
import pyautogui

def send_frame(self):
    try:
        frame_base64 = None
        with mss.mss() as sct:
            while self.remotedesktop and self.connected:
                try:
                    frame = sct.grab(sct.monitors[1])
                    img = Image.frombytes("RGB", frame.size, frame.rgb)
                    img = img.convert("RGB")
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG")
                    frame_data = buffer.getvalue()
                    frame_base64 = base64.b64encode(frame_data).decode("utf-8")
                    if frame_base64:
                        self.send_message('response', self.converter.encode({"remotedesktop": frame_base64}))
                        frame_base64 = None
                        continue
                    if not self.send_message('response', self.converter.encode({"remotedesktop_logger": f"From Client: No frame data found"})):
                        break
                except:
                    self.remotedesktop = False
                    self.send_message('response', self.converter.encode({"remotedesktop_logger": f"From Client: {traceback.format_exc()}"}))
                    break
    except:
        self.remotedesktop = False
        self.send_message('response', self.converter.encode({"remotedesktop_logger": f"From Client: {traceback.format_exc()}"}))

def get_click_coordinates(shared_data):
    try:
        x = shared_data.get("x")
        y = shared_data.get("y")
        screen_width, screen_height = pyautogui.size()
        click_x = int(x * screen_width)
        click_y = int(y * screen_height)
        return click_x, click_y
    except:
        return 0, 0

def perform_action(self):
    try:
        while self.remotedesktop and self.connected:
            try:
                shared_data = self.shared_data.get_shared_data("remotedesktop")
                if shared_data and shared_data.get("remotedesktop"):
                    event_data = shared_data.get("event_type")
                    key = shared_data.get("key")
                    if event_data in ["left_click", "right_click"]:
                        click_x, click_y = get_click_coordinates(shared_data)
                        if event_data == "left_click":
                            pyautogui.click(click_x, click_y)
                        elif event_data == "right_click":
                            pyautogui.rightClick(click_x, click_y)
                    elif event_data == "key_press":
                        if key:
                            if len(key) != 1:
                                pyautogui.keyDown(key)
                            else:
                                pyautogui.write(key)
                    elif event_data == "key_release":
                        if key and len(key) != 1:
                            pyautogui.keyUp(key)
            except:
                self.remotedesktop = False
                self.send_message('response', self.converter.encode({"remotedesktop_logger": f"From Client: {traceback.format_exc()}"}))
                break
    except:
        self.remotedesktop = False
        self.send_message('response', self.converter.encode({"remotedesktop_logger": f"From Client: {traceback.format_exc()}"}))
