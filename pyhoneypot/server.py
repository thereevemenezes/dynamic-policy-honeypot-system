import socket
import json
import datetime
import sys

HOST = "0.0.0.0"
PORT = 2223

def log_event(addr, data):
    event = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "src_ip": addr[0],
        "src_port": addr[1],
        "data": data,
    }
    print(json.dumps(event), flush=True)

def handle_client(conn, addr):
    # Send fake SSH banner
    fake_banner = "SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3\r\n"
    conn.sendall(fake_banner.encode())

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            log_event(addr, data.decode(errors="ignore"))

            # Fake response to make attacker think SSH is alive
            conn.sendall(b"Permission denied, please try again.\r\n")

    except Exception as e:
        log_event(addr, f"Exception: {e}")

    finally:
        conn.close()

def start_server():
    print(f"[*] PyTrap honeypot listening on {HOST}:{PORT}", flush=True)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            print(f"[+] Connection from {addr}", flush=True)
            handle_client(conn, addr)

if __name__ == "__main__":
    start_server()
