"""
Project: Traceroute Implementation
Author: Pra P.
Description:
    Cross-platform Python traceroute implementation.
    Uses UDP probes with increasing TTL and listens for ICMP "Time Exceeded" responses.
    Works on Windows (Admin mode) and Linux/macOS (root).

Usage:
    python traceroute.py <hostname>
"""

import sys
import time
import socket
import platform

MAX_HOPS = 30
TIMEOUT = 2.0
TRIES_PER_HOP = 3
DEST_PORT = 33434


def traceroute(dest_name):
    """Perform traceroute to the specified host."""
    try:
        dest_addr = socket.gethostbyname(dest_name)
    except socket.gaierror:
        print(f"Cannot resolve {dest_name}: Unknown host")
        return

    print(f"Tracing route to {dest_name} [{dest_addr}] with max {MAX_HOPS} hops:\n")

    for ttl in range(1, MAX_HOPS + 1):
        sys.stdout.write(f"{ttl:2d}  ")
        sys.stdout.flush()

        try:
            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except PermissionError:
            print("\nError: Run this program as Administrator (Windows) or root (Linux/macOS).")
            return

        recv_socket.settimeout(TIMEOUT)

        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # Windows uses IPPROTO_IP instead of SOL_IP for setsockopt
        level = socket.IPPROTO_IP if platform.system() == "Windows" else socket.SOL_IP
        send_socket.setsockopt(level, socket.IP_TTL, ttl)

        recv_socket.bind(("", DEST_PORT))

        curr_addr = None
        curr_name = None
        times = []

        for _ in range(TRIES_PER_HOP):
            start_time = time.time()
            send_socket.sendto(b"", (dest_addr, DEST_PORT))
            try:
                _, curr_addr = recv_socket.recvfrom(512)
                elapsed = (time.time() - start_time) * 1000
                curr_addr = curr_addr[0]
                times.append(f"{int(elapsed)} ms")
            except socket.timeout:
                times.append("*")

        send_socket.close()
        recv_socket.close()

        if curr_addr is not None:
            try:
                curr_name = socket.gethostbyaddr(curr_addr)[0]
            except socket.herror:
                curr_name = curr_addr
            display_name = f"{curr_name} ({curr_addr})"
        else:
            display_name = "Request timed out"

        print(f"{'  '.join(times)}  {display_name}")

        if curr_addr == dest_addr:
            print("\nTrace complete.")
            break


def main():
    if len(sys.argv) != 2:
        print("Usage: python traceroute.py <hostname>")
        sys.exit(1)

    dest_name = sys.argv[1]
    traceroute(dest_name)


if __name__ == "__main__":
    main()
