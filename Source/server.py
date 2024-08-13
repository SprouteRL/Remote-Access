import socket

class Server:
    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port

        self.sock = None
        self.bind()
    
    def bind(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.IP, self.PORT))

        self.sock.listen(1)
        print(f"Listening at {IP}:{PORT}")

        self.accept()
    
    def accept(self):
        conn, addr = self.sock.accept()

        conn.send(str("name").encode())
        data = conn.recv(1024).decode()

        print(f"welcome {data}")

        self.sock.close()
    
IP = "127.0.0.1"
PORT = 13063

Server(IP, PORT)