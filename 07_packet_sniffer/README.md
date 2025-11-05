# Packet Sniffer — README

## Overview

This project provides a simple packet sniffer implemented in Python.
It prefers using **Scapy** for capture and PCAP output. On Windows it will use a Layer-2 (Ethernet) capture if a libpcap provider (Npcap/WinPcap) is installed; otherwise it can fall back to Layer-3 (IP-level) capture. On Linux it falls back to an `AF_PACKET` raw socket if Scapy is not available.

The sniffer supports a small, BPF-style filter language for convenience (not full BPF):
examples: `tcp`, `udp`, `icmp`, `port 53`, `tcp and port 80`, `udp and port 53`.

---

## Files

* `sniffer.py` — main script (captures packets, prints metadata and short hex payload, optional PCAP output).

---

## Requirements

* Python 3.8+ (3.10+ recommended)
* `scapy` (recommended)

  ```bash
  pip install scapy
  ```
* (Optional, Windows) **Npcap** for full Layer-2 capture: [https://nmap.org/npcap/](https://nmap.org/npcap/)
  Install with **“WinPcap API-compatible mode”** enabled.

---

## How it behaves (summary)

* If Scapy + pcap provider present → uses L2 capture (Ethernet) (full features).
* If Scapy present but no pcap provider:

  * On Windows: script will require Administrator if using L3; otherwise it will print instructions to install Npcap or run elevated.
  * Use `--force-l3` to explicitly force L3 (IP-layer) capture (Administrator required on Windows).
* If Scapy not installed and platform is Linux → uses AF_PACKET raw socket (IPv4 only).
* If Scapy not installed and platform is Windows or other non-Linux → script exits with message to install Scapy.

---

## Command line usage

```
usage: sniffer.py [-h] [-i INTERFACE] [-f FILTER] [-c COUNT] [-o OUTPUT] [--force-l3]

Options:
  -i, --interface   Interface name to capture on (e.g., eth0, Ethernet). If omitted scapy chooses default.
  -f, --filter      Simple filter, e.g. "tcp and port 80" or "udp" or "port 53"
  -c, --count       Stop after capturing COUNT packets (default: 0 meaning run until Ctrl-C)
  -o, --output      Write captured packets to a PCAP file (requires Scapy)
  --force-l3        Force Scapy L3 (IP-layer) socket even if a pcap provider exists
```

---

## Recommended run commands

### On Windows — recommended long-term: install Npcap (no admin needed to run)

1. Install Npcap: [https://nmap.org/npcap/](https://nmap.org/npcap/)

   * During install enable *WinPcap API-compatible mode*.
2. Open PowerShell (normal or admin) and run:

```powershell
cd "C:\path\to\07_packet_sniffer"
python sniffer.py -f "udp and port 53" -c 5
```

### On Windows — quick (no Npcap) using IP-layer fallback (requires Administrator)

1. Open PowerShell **as Administrator** (right-click → Run as Administrator).
2. Run with forced L3:

```powershell
cd "C:\path\to\07_packet_sniffer"
python sniffer.py --force-l3 -f "udp and port 53" -c 5
```

> `--force-l3` captures at IP layer (no Ethernet headers). Administrator privileges are generally required for L3 raw sockets on Windows.

### On Linux

Either Scapy L2 capture works (with libpcap) or script falls back to AF_PACKET raw socket (needs root):

```bash
cd ~/projects/07_packet_sniffer
# If using Scapy+lpcap:
python sniffer.py -f "tcp and port 80" -c 50
# If Scapy not installed, run as root to allow raw socket fallback:
sudo python sniffer.py -f "tcp and port 80" -c 50
```

### Save capture to PCAP (requires Scapy)

```bash
python sniffer.py -f "tcp" -c 100 -o capture.pcap
```

Open `capture.pcap` with Wireshark.

---

## Quick tests to generate traffic (run while sniffer is capturing)

**DNS (UDP/53)**

```powershell
nslookup google.com          # Windows / PowerShell
# or
Resolve-DnsName google.com   # PowerShell
```

**HTTP (example non-HTTPS)**

```powershell
curl http://example.com
```

**Ping (ICMP)**

```bash
ping 8.8.8.8 -n 3    # Windows (or `ping -c 3 8.8.8.8` on Linux)
```

If you filter `udp and port 53`, use `nslookup`. If your system or browser uses DoH (DNS over HTTPS), `nslookup` still uses classic UDP DNS and is the correct test.

---

## Filter language (simple examples)

* `tcp` — all TCP packets
* `udp` — all UDP packets
* `icmp` — ICMP (ping) packets
* `port 53` — any packet with source or destination port 53 (TCP or UDP)
* `tcp and port 80` — TCP packets where either src or dst port is 80
* `udp and port 53` — UDP packets where either src or dst port is 53

This is a limited convenience parser. For complex filtering use Wireshark/tcpdump and PCAP files.

---

## Common errors and fixes

### `WARNING: No libpcap provider available ! pcap won't be used`

Means Scapy cannot find Npcap/WinPcap. Options:

* Install Npcap (recommended). Then re-run sniffer.
* Or use `--force-l3` and run as Administrator (Windows) to use IP-layer capture.

### `Scapy capture error: Windows native L3 Raw sockets are only usable as administrator`

* Run PowerShell as Administrator and re-run with `--force-l3`, or install Npcap and run normally.

### Script exits immediately with no packets

* No matching packets occurred while the sniffer was listening. Start sniffer first, then generate traffic (see tests above).
* If capturing with `-c N`, it will stop as soon as it captures N matching packets. For manual testing use no `-c` and Ctrl-C to stop.

### `Permission denied` (Linux `AF_PACKET`)

* Run with `sudo` or as root:

```bash
sudo python sniffer.py -f "tcp"
```

---

## Troubleshooting checklist

1. Did you install `scapy`?

   ```bash
   pip install scapy
   ```
2. On Windows: did you install Npcap? If not, use `--force-l3` and run PowerShell as Administrator (temporarily).
3. Start sniffer, then generate traffic with `nslookup`, `curl`, or `ping`.
4. If you still see nothing, try a broader capture:

   ```bash
   python sniffer.py --force-l3
   # then in another window: nslookup google.com
   ```
5. If you want to inspect later, run with `-o capture.pcap` and open that file in Wireshark.

---

## Security & privacy notes

* Sniffing network traffic may capture sensitive data. Only run this tool on networks where you have permission.
* PCAP files may contain credentials or personal data; secure or delete them when no longer needed.

---

## Example full Windows session (recommended quick start)

1. (Optional) Install scapy:

```powershell
pip install scapy
```

2. (Optional recommended) Install Npcap from [https://nmap.org/npcap/](https://nmap.org/npcap/)
3. Open PowerShell as Administrator (if not using Npcap):

   * Start → type `PowerShell` → right-click → *Run as administrator*
4. Start sniffer (force L3 if no Npcap):

```powershell
cd "C:\Users\Prash\Desktop\cn\assigment\07_packet_sniffer"
python sniffer.py --force-l3 -f "udp and port 53"
```

5. In another PowerShell window:

```powershell
nslookup google.com
```

6. Observe packets printed in the sniffer window. Stop sniffer with `Ctrl-C` when done.

---
