import socket, struct, time

def build_open():
    """Observer peer ASN must match the lab's configured remote-as 65003."""
    body = struct.pack('!BHH4sB', 4, 65003, 0, socket.inet_aton('10.0.0.2'), 0)
    return b'\xff' * 16 + struct.pack('!HB', 19 + len(body), 1) + body

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 1790))
    s.listen(1)
    print("Dummy BGP peer listening on 1790...")
    while True:
        conn = None
        try:
            conn, addr = s.accept()
            print("Accepted connection from", addr)
            # Send OPEN
            open_msg = build_open()
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
        finally:
            if conn is not None:
                conn.close()

if __name__ == "__main__":
    main()
