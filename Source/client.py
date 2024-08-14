import socket

IP = "127.0.0.1"
PORT = 13064

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP, PORT))
    print(f"Connected to {IP}:{PORT}")

    while True:
        data = sock.recv(1024).decode()
        if data == "name":
            sock.send(socket.gethostname().encode())
        elif data == "exit":
            sock.close()
            exit(0)
        else:
            print(data)
except KeyboardInterrupt:
    print("\nClosing socket.")
    sock.close()
    exit(0)
