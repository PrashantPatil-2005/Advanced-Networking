## `02_traceroute/README.md`

# Traceroute Implementation

## Overview
This project implements the functionality of the classic `traceroute` utility in Python.  
It uses UDP packets with incrementally increasing TTL (Time To Live) values and listens for ICMP "Time Exceeded" responses to identify each router hop between the local host and the destination.

---

## Features
- Sends UDP probes with increasing TTL values  
- Captures ICMP "Time Exceeded" responses from routers  
- Displays IP addresses and round-trip times for each hop  
- Stops automatically when the destination is reached  
- Pure Python implementation using raw sockets (no external libraries)

---

## Concepts Demonstrated
- Use of raw sockets in Python  
- ICMP and UDP packet structure  
- Manipulating the IP header’s TTL field  
- Measuring latency using timestamps  
- Parsing and interpreting network responses

---

## How It Works
1. The program sends UDP packets to the destination with TTL starting at 1.  
2. Each router that decrements the TTL to 0 returns an ICMP "Time Exceeded" message.  
3. The source IP address of this ICMP packet identifies that router.  
4. TTL is incremented and the process repeats until the destination responds.  
5. The round-trip time for each hop is measured and displayed.

---

## How to Run

You need **administrator/root privileges** to create raw sockets.

### 1. Run the Program
```bash
sudo python traceroute.py <destination_host>
````

Example:

```bash
sudo python traceroute.py google.com
```

Expected output:

```
Tracing route to google.com [142.250.183.206]
1    1 ms    192.168.1.1
2    8 ms    10.0.0.1
3   20 ms    142.250.183.206
Trace complete.
```

---

## Example Output

```
Tracing route to example.com [93.184.216.34]
1    2 ms    192.168.1.1
2   10 ms    172.217.0.1
3   22 ms    93.184.216.34
Trace complete.
```

---

## File Structure

```
02_traceroute/
│
├── traceroute.py   # UDP-based traceroute implementation
└── README.md       # Project documentation
```

---

## Requirements

* Python 3.10 or higher
* Root or administrator privileges
* Works on Linux, macOS, or Windows (with admin access)

---

## Future Improvements

* Support for both ICMP and UDP modes
* Add option for parallel probing to speed up execution
* Implement hostname resolution with `gethostbyaddr`
* Add plotting of latency per hop using Matplotlib

