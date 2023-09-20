import io
import socket
import struct
import time
import picamera

# Create a socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8000))  # Listen on all available network interfaces
server_socket.listen(0)

print("Server is listening...")

# Accept a connection from a client
client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address}")

try:
    with picamera.PiCamera() as camera:
        camera.resolution = (320, 240)  # Pi camera resolution
        camera.framerate = 15           # 15 frames/sec
        time.sleep(2)                  # Give 2 seconds for the camera to initialize
        start = time.time()
        stream = io.BytesIO()

        # Send JPEG format video stream
        for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            connection = client_socket.makefile('wb')
            try:
                connection.write(struct.pack('<L', stream.tell()))
                connection.flush()
                stream.seek(0)
                connection.write(stream.read())
            finally:
                connection.close()
            
            if time.time() - start > 600:  # Stop streaming after 600 seconds (10 minutes)
                break
            
            stream.seek(0)
            stream.truncate()

finally:
    client_socket.close()
    server_socket.close()