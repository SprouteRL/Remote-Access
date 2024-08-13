import socket

IP = "127.0.0.1"
PORT = 13063

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP, PORT))

print(f"Connected to {IP}:{PORT}")

data = sock.recv(1024).decode()
if data == "name":
    sock.send(socket.gethostname().encode())

sock.close()