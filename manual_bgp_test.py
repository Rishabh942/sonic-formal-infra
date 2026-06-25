import socket
import time

def main():
    target_ip = "127.0.0.1"
    target_port = 1179

    print(f"Connecting to {target_ip}:{target_port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    
    try:
        s.connect((target_ip, target_port))
        print("Connected! Sending a valid BGP UPDATE packet immediately (without OPEN)...")
        
        # BGP Marker (16 bytes 0xFF)
        marker = b'\xff' * 16
        # Length (2 bytes): 23
        length = b'\x00\x17'
        # Type (1 byte): 2 (UPDATE)
        type_code = b'\x02'
        # Withdrawn Routes Length: 0
        w_len = b'\x00\x00'
        # Path Attributes Length: 0
        pa_len = b'\x00\x00'
        
        update_packet = marker + length + type_code + w_len + pa_len
        s.sendall(update_packet)
        print("Packet sent. Waiting for response or disconnect...")
        
        # Now wait to see if we get a NOTIFICATION or if it hangs open
        try:
            data = s.recv(4096)
            if data:
                print(f"Received {len(data)} bytes from FRR: {data.hex()}")
            else:
                print("Connection closed gracefully by FRR (0 bytes read).")
        except socket.timeout:
            print("Socket timeout! FRR kept the connection open and sent nothing.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        s.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()
