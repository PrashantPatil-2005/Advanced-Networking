"""
06_dns_query_builder_parser.py
--------------------------------
A low-level DNS client that crafts a raw UDP query for A-record lookups,
sends it to a DNS server, and parses the binary response.

This project demonstrates:
- DNS message format
- UDP socket communication
- Manual byte-level parsing of DNS responses
"""

import random
import socket
import struct


def build_dns_query(domain_name):
    """Build a raw DNS query packet for an A record lookup."""
    # Transaction ID: 2 bytes random
    transaction_id = random.randint(0, 65535)
    flags = 0x0100  # standard query with recursion desired
    qdcount = 1     # one question
    ancount = 0
    nscount = 0
    arcount = 0

    # Header section (12 bytes)
    header = struct.pack(">HHHHHH", transaction_id, flags, qdcount, ancount, nscount, arcount)

    # Question section
    qname = b''.join(
        struct.pack("B", len(part)) + part.encode() for part in domain_name.split('.')
    ) + b'\x00'  # terminate QNAME with null byte
    qtype = 1   # Type A
    qclass = 1  # IN (Internet)
    question = qname + struct.pack(">HH", qtype, qclass)

    return transaction_id, header + question


def parse_dns_response(data, transaction_id):
    """Parse the binary DNS response."""
    (resp_id, flags, qdcount, ancount, nscount, arcount) = struct.unpack(">HHHHHH", data[:12])
    if resp_id != transaction_id:
        raise ValueError("Transaction ID mismatch in response.")

    print("\n--- DNS Response ---")
    print(f"Transaction ID: {resp_id}")
    print(f"Flags: 0x{flags:04x}")
    print(f"Questions: {qdcount}, Answers: {ancount}")

    # Skip the question section
    offset = 12
    for _ in range(qdcount):
        while data[offset] != 0:
            offset += 1 + data[offset]
        offset += 5  # null byte + QTYPE (2) + QCLASS (2)

    print("\nResolved A Records:")
    for _ in range(ancount):
        start_offset = offset
        # Handle pointer (0xC0 means name compression)
        if data[offset] & 0xC0 == 0xC0:
            offset += 2
        else:
            while data[offset] != 0:
                offset += 1 + data[offset]
            offset += 1

        rtype, rclass, ttl, rdlength = struct.unpack(">HHIH", data[offset:offset + 10])
        offset += 10

        rdata = data[offset:offset + rdlength]
        offset += rdlength

        if rtype == 1 and rclass == 1 and rdlength == 4:  # A record
            ip_addr = '.'.join(map(str, rdata))
            print(f"IP: {ip_addr}, TTL: {ttl}s")
        else:
            print(f"Non-A record (type {rtype}), skipped.")


def dns_lookup(domain, dns_server="8.8.8.8"):
    """Send DNS query and print parsed response."""
    transaction_id, query_packet = build_dns_query(domain)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    server_addr = (dns_server, 53)

    print(f"\nSending DNS query for '{domain}' to {dns_server}...")
    sock.sendto(query_packet, server_addr)

    try:
        data, _ = sock.recvfrom(512)
        parse_dns_response(data, transaction_id)
    except socket.timeout:
        print("Request timed out.")
    finally:
        sock.close()


def main():
    domain = input("Enter domain to resolve (e.g., google.com): ").strip()
    dns_lookup(domain)


if __name__ == "__main__":
    main()
