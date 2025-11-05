# VLSM Subnet Allocator

## Overview

This project implements a **Variable Length Subnet Mask (VLSM)** allocator in Python.
It divides a given base IPv4 network (e.g., `192.168.0.0/24`) into multiple subnets of different sizes based on user-provided host requirements.

The allocator ensures:

* Efficient use of IP address space (largest subnets allocated first)
* Proper alignment to subnet boundaries
* Accurate calculation of usable host addresses, broadcast addresses, and subnet masks

---

## Features

* Accepts base network and required host counts via CLI or interactive mode
* Automatically determines the smallest possible subnet for each host requirement
* Displays a formatted allocation table
* Optionally exports results to a CSV file
* Uses only Python’s standard library (no external dependencies)

---

## Requirements

* **Python 3.8+**
* No external libraries required (uses `ipaddress`, `math`, `csv`, `argparse`)

---

## Files

| File          | Description                                                      |
| ------------- | ---------------------------------------------------------------- |
| `vlsm.py`     | Main script for VLSM allocation                                  |
| `results.csv` | (Optional) Generated CSV file containing subnet allocation table |

---

## How It Works

1. You provide a base network (in CIDR notation, e.g., `192.168.10.0/24`).
2. You provide a list of required host counts for each subnet (e.g., `50,20,10,5`).
3. The allocator:

   * Sorts subnets largest-first (to minimize wasted addresses).
   * Determines prefix length needed for each subnet.
   * Assigns each subnet sequentially inside the base network.
   * Prints a detailed allocation table.

---

## Usage

### **A. Interactive Mode**

```bash
python vlsm.py
```

Example session:

```
Enter base network (CIDR), e.g. 192.168.0.0/24: 192.168.10.0/24
Enter required hosts per subnet (comma-separated), e.g. 50,20,10,5: 50,20,10,5
```

Output:

```
Base network: 192.168.10.0/24

ID     Network/CIDR       Prefix Netmask         First           Last            Broadcast       Total Usable
-------------------------------------------------------------------------------------------------------------
1      192.168.10.0/26    /26    255.255.255.192 192.168.10.1    192.168.10.62   192.168.10.63   64    62
2      192.168.10.64/27   /27    255.255.255.224 192.168.10.65   192.168.10.94   192.168.10.95   32    30
3      192.168.10.96/28   /28    255.255.255.240 192.168.10.97   192.168.10.110  192.168.10.111  16    14
4      192.168.10.112/29  /29    255.255.255.248 192.168.10.113  192.168.10.118  192.168.10.119  8     6
```

---

### **B. Command-Line Mode (Non-Interactive)**

```bash
python vlsm.py --network 192.168.10.0/24 --hosts 50,20,10,5
```

---

### **C. Export Results to CSV**

```bash
python vlsm.py --network 192.168.10.0/24 --hosts 50,20,10,5 --output results.csv
```

This will create a CSV file with columns:

```
subnet_id, cidr, prefix, network, netmask, first_usable, last_usable,
broadcast, total_addresses, usable_hosts, requested_hosts
```

---

## Example CSV Output (`results.csv`)

| subnet_id | cidr              | prefix | network        | netmask         | first_usable   | last_usable    | broadcast      | total_addresses | usable_hosts | requested_hosts |
| --------- | ----------------- | ------ | -------------- | --------------- | -------------- | -------------- | -------------- | --------------- | ------------ | --------------- |
| 1         | 192.168.10.0/26   | /26    | 192.168.10.0   | 255.255.255.192 | 192.168.10.1   | 192.168.10.62  | 192.168.10.63  | 64              | 62           | 50              |
| 2         | 192.168.10.64/27  | /27    | 192.168.10.64  | 255.255.255.224 | 192.168.10.65  | 192.168.10.94  | 192.168.10.95  | 32              | 30           | 20              |
| 3         | 192.168.10.96/28  | /28    | 192.168.10.96  | 255.255.255.240 | 192.168.10.97  | 192.168.10.110 | 192.168.10.111 | 16              | 14           | 10              |
| 4         | 192.168.10.112/29 | /29    | 192.168.10.112 | 255.255.255.248 | 192.168.10.113 | 192.168.10.118 | 192.168.10.119 | 8               | 6            | 5               |

---

## Example Command Summary

| Task                   | Command                                                                            |
| ---------------------- | ---------------------------------------------------------------------------------- |
| Run interactively      | `python vlsm.py`                                                                   |
| Run with CLI arguments | `python vlsm.py --network 192.168.10.0/24 --hosts 50,20,10,5`                      |
| Export to CSV          | `python vlsm.py --network 192.168.10.0/24 --hosts 50,20,10,5 --output results.csv` |
| Show help              | `python vlsm.py -h`                                                                |

---

## Troubleshooting

| Issue                        | Cause                                                            | Solution                                               |
| ---------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------ |
| `Invalid base network`       | CIDR format incorrect                                            | Use a proper CIDR (e.g., `192.168.1.0/24`)             |
| `Invalid hosts list`         | Host counts not numeric                                          | Enter only comma-separated integers (e.g., `50,20,10`) |
| `Insufficient address space` | Requested subnets exceed network capacity                        | Use a larger base network or reduce host requirements  |
| Nothing prints               | Ensure you provided valid input or proper command-line arguments |                                                        |

---

## Example Scenarios

### Example 1:

```bash
python vlsm.py --network 10.0.0.0/24 --hosts 60,20,10,5
```

Allocates:

* /26 for 60 hosts
* /27 for 20 hosts
* /28 for 10 hosts
* /29 for 5 hosts

### Example 2:

```bash
python vlsm.py --network 192.168.5.0/26 --hosts 30,20,10
```

Will raise:

```
Allocation error: Insufficient address space: cannot allocate /29 for 10 hosts inside 192.168.5.0/26
```

---

## Security Note

This script performs **local calculations only**.
It does not interact with networks or send any packets. Safe to run on any system.


