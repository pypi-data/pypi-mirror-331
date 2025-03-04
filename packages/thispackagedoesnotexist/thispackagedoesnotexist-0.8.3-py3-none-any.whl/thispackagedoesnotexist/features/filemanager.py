import traceback
import os
import io
import base64
import gzip
import shutil
import tempfile
import uuid
from ..plugins.chunks import read_file_in_chunks, CHUNK_SIZE

def file_manager(self, data):
    try:
        action = data.get("action")
        if action:
            filename = data.get("file_name")
            if action == "download":
                path = self.fm._get_download(filename)
                if not path: 
                    self.send_message('response', self.converter.encode({"filemanager_logger": f"From Client: Not found: {path}"}))
                    return
            
                total_size = os.path.getsize(path) if os.path.isfile(path) else None
                file_name = os.path.basename(path)

                if os.path.isfile(path):
                    with open(path, "rb") as f:

                        for chunk, is_last in read_file_in_chunks(f, CHUNK_SIZE):

                            buffer = io.BytesIO()
                            with gzip.GzipFile(fileobj=buffer, mode="wb") as gz:
                                gz.write(chunk)
                            compressed_chunk = buffer.getvalue()

                            encoded_chunk = base64.b64encode(compressed_chunk).decode('utf-8')

                            data = {
                                'file_name': file_name,
                                'chunk': encoded_chunk,
                                'chunk_size': len(chunk),
                                'total_size': total_size,
                                'is_last': is_last,
                            }

                            if not self.send_message('download', self.converter.encode({"filemanager": data})):
                                break

                elif os.path.isdir(path):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_zip_path = os.path.join(temp_dir, str(uuid.uuid4()))
                        shutil.make_archive(temp_zip_path, 'zip', path)

                        with open(f"{temp_zip_path}.zip", "rb") as f:
                            temp_zip = io.BytesIO(f.read())

                    temp_zip.seek(0)
                    total_size = temp_zip.getbuffer().nbytes

                    for chunk, is_last in read_file_in_chunks(temp_zip, CHUNK_SIZE):
                        buffer = io.BytesIO()
                        with gzip.GzipFile(fileobj=buffer, mode="wb") as gz:
                            gz.write(chunk)
                        compressed_chunk = buffer.getvalue()

                        encoded_chunk = base64.b64encode(compressed_chunk).decode('utf-8')

                        data = {
                            'file_name': f"{file_name}.zip",
                            'chunk': encoded_chunk,
                            'chunk_size': len(chunk),
                            'total_size': total_size,
                            'is_last': is_last,
                        }

                        if not self.send_message('download', self.converter.encode({"filemanager": data})):
                            break

            elif action == "open":
                status, response = self.fm._open_file(filename)
                self.send_message('response', self.converter.encode({"filemanager_logger": f"From Client: {response}"}))
            
            elif action == "delete":
                status, response = self.fm._delete_file(filename)
                self.send_message('response', self.converter.encode({"filemanager_logger": f"From Client: {response}"}))

            elif action == "rename":
                new_name = data.get("new_name")
                status, response = self.fm._rename_file(filename, new_name)
                self.send_message('response', self.converter.encode({"filemanager_logger": f"From Client: {response}"}))

            elif action == "extract":
                status, response = self.fm._extract_file(filename)
                self.send_message('response', self.converter.encode({"filemanager_logger": f"From Client: {response}"}))

            elif action == "compress":
                status, response = self.fm._compress_file(filename)
                self.send_message('response', self.converter.encode({"filemanager_logger": f"From Client: {response}"}))

        else:
            status, entries = self.fm.navigate_path(data)
            if not status:
                self.send_message('response', self.converter.encode({"filemanager_logger": f"From Client: {entries}"}))
                return

            self.send_message('response', self.converter.encode({"filemanager": entries}))

    except:
        self.send_message('response', self.converter.encode({"filemanager_logger": f"From Client: {traceback.format_exc()}"}))
