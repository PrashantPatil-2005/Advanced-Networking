#!/usr/bin/env python3
"""
sniffer.py

Packet sniffer with simple BPF-style filters and an explicit L3 (IP-layer) fallback for Windows.

This version adds a robust Windows admin check to avoid using Scapy L3 sockets
on Windows when the process is not elevated (which previously produced the
"Windows native L3 Raw sockets are only usable as administrator" error and
a destructor traceback).

Usage examples:
    python sniffer.py -f "udp and port 53" -c 5
    python sniffer.py --force-l3 -f "udp and port 53" -c 5
"""

from __future__ import annotations
import argparse
import datetime
import sys
import textwrap
import platform
import os
import binascii
import struct
import socket

# Try to import scapy. If unavailable, we'll fall back to raw sockets on Linux.
USE_SCAPY = False
SCAPY_HAS_PCAP = False
try:
    from scapy.all import sniff, Raw, IP, IPv6, TCP, UDP, ICMP, wrpcap, conf
    USE_SCAPY = True
    try:
        SCAPY_HAS_PCAP = bool(getattr(conf, "use_pcap", False))
    except Exception:
        SCAPY_HAS_PCAP = False
except Exception:
    USE_SCAPY = False
    SCAPY_HAS_PCAP = False

# -------------------------
# Helper: check admin/elevation on Windows
# -------------------------
def is_admin() -> bool:
    """Return True if running with admin rights on Windows, or root on Unix."""
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        # On Unix-like systems, root UID is 0
        try:
            return os.geteuid() == 0
        except AttributeError:
            return False

# -------------------------
# Simple BPF-style filter parsing
# -------------------------
def parse_simple_filter(filter_str: str) -> dict:
    """Return a dict with filter criteria parsed from filter_str."""
    criteria = {"proto": None, "port": None}
    if not filter_str:
        return criteria
    s = filter_str.lower().strip()
    parts = [p.strip() for p in s.split("and")]
    for p in parts:
        if p in ("tcp", "udp", "icmp"):
            criteria["proto"] = p
        elif p.startswith("port "):
            try:
                criteria["port"] = int(p.split()[1])
            except Exception:
                raise ValueError(f"Invalid port in filter: {p}")
        elif p.isdigit():
            criteria["port"] = int(p)
        else:
            raise ValueError(f"Unsupported filter token: '{p}'")
    return criteria

# -------------------------
# Utilities
# -------------------------
def short_hex_dump(data: bytes, length=32) -> str:
    if not data:
        return ""
    s = binascii.hexlify(data[:length]).decode()
    spaced = " ".join(textwrap.wrap(s, 2))
    if len(data) > length:
        spaced += " ..."
    return spaced

def ts() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

# -------------------------
# Scapy-based packet handler
# -------------------------
def make_scapy_callback(criteria: dict, pcap_list: list | None = None):
    def _callback(pkt):
        try:
            proto = None
            src = dst = sport = dport = "-"
            length = len(pkt)

            if IP in pkt:
                ip = pkt[IP]
                src = ip.src
                dst = ip.dst
            elif IPv6 in pkt:
                ip = pkt[IPv6]
                src = ip.src
                dst = ip.dst

            if TCP in pkt:
                proto = "tcp"
                sport = pkt[TCP].sport
                dport = pkt[TCP].dport
            elif UDP in pkt:
                proto = "udp"
                sport = pkt[UDP].sport
                dport = pkt[UDP].dport
            elif ICMP in pkt:
                proto = "icmp"

            # Apply simple filter
            if criteria["proto"] and proto != criteria["proto"]:
                return
            if criteria["port"] and (criteria["port"] not in (sport, dport)):
                return

            payload = bytes(pkt[Raw].load) if Raw in pkt else b""
            print(f"[{ts()}] {src}:{sport} -> {dst}:{dport}  {proto or 'other'}  len={length}")
            if payload:
                print("    payload (hex):", short_hex_dump(payload, length=48))
            if pcap_list is not None:
                pcap_list.append(pkt)
        except Exception as e:
            print("Error handling packet:", e, file=sys.stderr)
    return _callback

# -------------------------
# Linux raw socket fallback (simple IPv4 only)
# -------------------------
def linux_raw_socket_capture(iface: str | None, criteria: dict, count: int):
    """Capture using AF_PACKET raw socket (Linux). IPv4 only."""
    try:
        raw_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    except PermissionError:
        print("Permission denied: run as root to open raw socket.", file=sys.stderr)
        return
    except Exception as e:
        print("Failed to create AF_PACKET socket:", e, file=sys.stderr)
        return

    if iface:
        try:
            raw_sock.bind((iface, 0))
        except Exception as e:
            print(f"Failed to bind to interface {iface}: {e}", file=sys.stderr)
            raw_sock.close()
            return

    captured = 0
    print("Listening (Linux raw socket)... Press Ctrl-C to stop.")
    try:
        while True:
            pkt, addr = raw_sock.recvfrom(65535)
            captured += 1

            # Ethernet header: 14 bytes
            if len(pkt) < 14 + 20:
                continue
            eth_header = pkt[:14]
            eth_proto = struct.unpack("!H", eth_header[12:14])[0]
            if eth_proto != 0x0800:  # IPv4 only
                continue

            ip_header = pkt[14:34]
            iph = struct.unpack("!BBHHHBBH4s4s", ip_header)
            version_ihl = iph[0]
            iph_length = (version_ihl & 0x0F) * 4
            proto = iph[6]
            src_ip = socket.inet_ntoa(iph[8])
            dst_ip = socket.inet_ntoa(iph[9])

            proto_name = {6: "tcp", 17: "udp", 1: "icmp"}.get(proto, str(proto))
            sport = dport = "-"
            payload = b""

            ip_payload_offset = 14 + iph_length
            if proto == 6 and len(pkt) >= ip_payload_offset + 4:
                tcp_header = pkt[ip_payload_offset:ip_payload_offset+20]
                tcph = struct.unpack("!HH", tcp_header[:4])
                sport, dport = tcph
                payload = pkt[ip_payload_offset + 20:]
            elif proto == 17 and len(pkt) >= ip_payload_offset + 8:
                udph = struct.unpack("!HH", pkt[ip_payload_offset:ip_payload_offset+8])
                sport, dport = udph
                payload = pkt[ip_payload_offset + 8:]
            else:
                payload = pkt[ip_payload_offset:]

            # Apply filter
            if criteria["proto"] and criteria["proto"] != proto_name:
                continue
            if criteria["port"] and criteria["port"] not in (sport, dport):
                continue

            print(f"[{ts()}] {src_ip}:{sport} -> {dst_ip}:{dport}  {proto_name}  len={len(pkt)}")
            if payload:
                print("    payload (hex):", short_hex_dump(payload, length=48))

            if count and captured >= count:
                break

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        raw_sock.close()

# -------------------------
# CLI and orchestration
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Packet sniffer with simple BPF-style filters.")
    parser.add_argument("-i", "--interface", help="Interface to capture on (e.g., eth0 or 'Ethernet'). If omitted, scapy chooses default.")
    parser.add_argument("-f", "--filter", help='Simple filter, e.g. "tcp and port 80" or "udp" or "port 53"')
    parser.add_argument("-c", "--count", type=int, help="Stop after capturing COUNT packets", default=0)
    parser.add_argument("-o", "--output", help="Write captured packets to a PCAP file (requires Scapy).")
    parser.add_argument("--force-l3", action="store_true", help="Force Scapy L3 (IP-layer) socket even if a pcap provider exists.")
    args = parser.parse_args()

    # Parse filter
    try:
        criteria = parse_simple_filter(args.filter) if args.filter else {"proto": None, "port": None}
    except ValueError as e:
        print("Filter parse error:", e, file=sys.stderr)
        sys.exit(1)

    # Privilege hint
    if platform.system() != "Windows":
        try:
            if os.geteuid() != 0:
                print("Warning: you are not root. Capturing raw packets typically requires root privileges.", file=sys.stderr)
        except AttributeError:
            pass

    # If Scapy available:
    if USE_SCAPY:
        # If interface provided, set scapy conf if possible
        if args.interface:
            try:
                conf.iface = args.interface
            except Exception:
                pass

        pcap_list = [] if args.output else None
        callback = make_scapy_callback(criteria, pcap_list)

        # Decide capture mode: prefer L2 only if pcap provider exists and not forced L3
        use_l2 = SCAPY_HAS_PCAP and not args.force_l3

        # Windows-specific checks
        if platform.system() == "Windows":
            if SCAPY_HAS_PCAP:
                # Npcap available - user can still run non-admin if configured; proceed to L2 unless forced
                pass
            else:
                # No pcap provider installed
                if args.force_l3:
                    # User asked to force L3: ensure running elevated
                    if not is_admin():
                        print("Error: Forced L3 capture on Windows requires Administrator privileges.")
                        print("Please run PowerShell/CMD as Administrator or install Npcap for L2 capture.")
                        sys.exit(1)
                    else:
                        use_l2 = False  # L3 is allowed because we are admin
                else:
                    # Auto fallback path: do not attempt L3 if not admin (avoids Scapy crash)
                    if not is_admin():
                        print("Scapy detected but no Npcap/WinPcap found and process is not elevated.")
                        print("Options:")
                        print("  1) Install Npcap (https://nmap.org/npcap/) and run the script as Administrator for full L2 capture.")
                        print("  2) Run this script as Administrator with --force-l3 to use IP-layer capture.")
                        sys.exit(1)
                    else:
                        # Admin and no pcap: OK to use L3
                        use_l2 = False

        # If user forced L3, override
        if args.force_l3:
            use_l2 = False

        try:
            print("Starting capture using Scapy. Press Ctrl-C to stop.")
            if use_l2:
                # L2 capture (requires Npcap / libpcap)
                sniff(prn=callback, store=False, count=args.count or 0, iface=(args.interface if args.interface else None))
            else:
                # L3 capture (no Npcap required but on Windows requires admin -> we checked earlier)
                sniff(prn=callback, store=False, count=args.count or 0, iface=(args.interface if args.interface else None), L2socket=conf.L3socket)
        except KeyboardInterrupt:
            print("\nCapture stopped by user.")
        except Exception as e:
            # Provide actionable message for common Windows missing-pcap case
            if "winpcap" in str(e).lower() or "npcap" in str(e).lower() or "pcap" in str(e).lower():
                print("Scapy capture error:", e, file=sys.stderr)
                print("Hint: On Windows install Npcap (https://nmap.org/npcap/) for full L2 capture.")
                print("Or run as Administrator with --force-l3 to force IP-layer capture.")
            else:
                print("Scapy capture error:", e, file=sys.stderr)

        # If saving pcap and we collected packets, write them
        if args.output and pcap_list is not None:
            try:
                wrpcap(args.output, pcap_list)
                print(f"Wrote {len(pcap_list)} packets to {args.output}")
            except Exception as e:
                print("Failed to write PCAP:", e, file=sys.stderr)

    else:
        # Fallback to Linux raw socket capture
        if platform.system() == "Linux":
            linux_raw_socket_capture(args.interface, criteria, args.count)
        else:
            print("Scapy is not installed and no raw-socket fallback is available on this platform.", file=sys.stderr)
            print("Install scapy (pip install scapy) or run on Linux with root privileges.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
