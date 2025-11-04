## 06_dns_query_builder_parser — DNS Query Builder and Parser

### Overview

This project implements a **low-level DNS client** in Python that builds and sends a **raw UDP query** for an **A-record lookup** (IPv4 address) and manually parses the binary response — without using high-level libraries such as `dnspython`.

It demonstrates how DNS works at the **packet level**, including message formatting, UDP transmission, and response parsing.

---

### Features

* Constructs **raw DNS packets** (header + question section) manually.
* Sends UDP queries directly to a DNS server (default: `8.8.8.8`).
* Parses binary responses to extract:

  * Transaction ID
  * Flags
  * Number of questions and answers
  * A-record IP addresses and TTLs
* Handles **DNS name compression** (pointer-based names).
* Uses only Python’s built-in `socket` and `struct` modules.
* Demonstrates the **core structure** of DNS messages and UDP-based name resolution.

---

### File

* `dns_query_builder_parser.py` — Main script for DNS query and parsing.

---

### How It Works

1. The program builds a DNS query packet with:

   * A random **transaction ID**
   * Flags set for a **standard recursive query**
   * One **question section** for the domain name
2. It sends the query to the DNS server over **UDP port 53**.
3. Upon receiving the response, it:

   * Verifies the **transaction ID**
   * Parses the DNS **header and answer section**
   * Extracts **A-records** and displays corresponding IP addresses.

---

### Usage

#### Run the script

```bash
python dns_query_builder_parser.py
```

#### Example session

```
Enter domain to resolve (e.g., google.com): google.com

Sending DNS query for 'google.com' to 8.8.8.8...

--- DNS Response ---
Transaction ID: 12345
Flags: 0x8180
Questions: 1, Answers: 1

Resolved A Records:
IP: 142.250.183.206, TTL: 60s
```

---

### Configuration

You can change the DNS server (default is Google DNS) by editing this line:

```python
dns_lookup(domain, dns_server="8.8.8.8")
```

Or, pass another server such as:

```python
dns_lookup("example.com", dns_server="1.1.1.1")
```

---

### Concepts Demonstrated

| Concept                 | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| **DNS Query Structure** | Shows how headers, flags, and sections form a DNS packet.    |
| **UDP Communication**   | DNS queries and responses typically use UDP port 53.         |
| **Name Compression**    | DNS uses pointers (0xC0) to shorten repetitive names.        |
| **A-record Lookup**     | Retrieves IPv4 addresses associated with domain names.       |
| **Binary Parsing**      | Uses the `struct` module to unpack raw bytes from responses. |

---

### Requirements

* Python 3.7+
* Internet connection (since queries are sent live)
* No external libraries required

---

### References

* RFC 1035 — *Domain Names: Implementation and Specification*
* Tanenbaum, A. S. — *Computer Networks*
* Forouzan, B. — *Data Communications and Networking*


