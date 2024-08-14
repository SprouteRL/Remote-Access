import socket

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
            data = conn.recv(1024).decode()
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

                data = conn.recv(1024).decode()
                print(data)
        except KeyboardInterrupt:
            self.cleanup(conn)
    
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
