CHUNK_SIZE = 512 * 1024

def read_file_in_chunks(file_obj, chunk_size):
    counter = 0
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        counter += 1
        yield chunk, len(chunk) < chunk_size