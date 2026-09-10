import socket, struct, time

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 1790))
    s.listen(1)
    print("Dummy BGP peer listening on 1790...")
    while True:
        try:
            conn, addr = s.accept()
            print("Accepted connection from", addr)
            # Send OPEN
            open_msg = b'\xff'*16 + struct.pack('!HB', 29, 1) + b'\x04\xfe\x09\x00\x5a\x0a\x00\x00\x02\x00'
            conn.sendall(open_msg)
            # Receive OPEN
            conn.recv(4096)
            # Send KEEPALIVE
            conn.sendall(b'\xff'*16 + struct.pack('!HB', 19, 4))
            # Receive forever
            while True:
                data = conn.recv(4096)
                if not data: break
        except Exception as e:
            print("Error", e)

if __name__ == "__main__":
    main()
