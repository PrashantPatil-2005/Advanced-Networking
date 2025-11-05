#!/usr/bin/env python3
"""
vlsm.py

Variable Length Subnet Mask (VLSM) allocator.

Given a base IPv4 network (CIDR) and a list of required host counts for subnets,
this script allocates subnets in a way that minimizes wasted addresses using
VLSM (largest-first allocation).

Usage (interactive):
    python vlsm.py

Usage (CLI):
    python vlsm.py --network 192.168.0.0/24 --hosts 50,20,10,5 --output result.csv

Outputs a table of allocated subnets with:
 - Subnet ID (order)
 - Network address
 - Prefix (e.g., /26)
 - Netmask (e.g., 255.255.255.192)
 - First usable IP
 - Last usable IP
 - Broadcast address
 - Total addresses
 - Usable hosts (total - 2)
 - Requested hosts

Requirements:
 - Python 3.8+
 - Uses only stdlib (ipaddress, csv, argparse)
"""

from __future__ import annotations
import argparse
import ipaddress
import math
import csv
from typing import List, Tuple, Dict


def hosts_to_prefix(required_hosts: int) -> int:
    """
    Given required usable hosts (requested hosts), return the smallest prefix length
    that can contain them (accounts for network and broadcast addresses).
    """
    if required_hosts < 1:
        raise ValueError("Requested hosts must be >= 1")
    # Need total addresses = required_hosts + 2 (network + broadcast)
    needed = required_hosts + 2
    # find smallest power of two >= needed
    bits = math.ceil(math.log2(needed))
    total_addresses = 2 ** bits
    prefix = 32 - bits
    return prefix


def allocate_vlsm(base_net: ipaddress.IPv4Network, requirements: List[int]) -> List[Dict]:
    """
    Allocate subnets for each requirement (list of requested host counts).
    Returns list of dicts with allocation details in the order allocated (largest-first).
    """
    # Sort requirements descending along with their original index (to preserve identity)
    reqs = sorted(
        [(req, idx) for idx, req in enumerate(requirements)],
        key=lambda x: (-x[0], x[1]),
    )

    allocations: List[Tuple[int, ipaddress.IPv4Network, int]] = []  # (orig_idx, subnet, requested)

    current_address = int(base_net.network_address)
    last_address = int(base_net.broadcast_address)

    for req_hosts, orig_idx in reqs:
        prefix = hosts_to_prefix(req_hosts)
        # Create candidate network at current_address with that prefix (strict=False allows non-aligned)
        try:
            candidate = ipaddress.IPv4Network((current_address, prefix), strict=False)
        except Exception as e:
            raise RuntimeError(f"Failed to create subnet for {req_hosts} hosts at {ipaddress.IPv4Address(current_address)}: {e}")

        # Ensure the subnet fits inside base network
        if int(candidate.network_address) < int(base_net.network_address) or int(candidate.broadcast_address) > last_address:
            raise RuntimeError(
                f"Insufficient address space: cannot allocate /{prefix} for {req_hosts} hosts inside {base_net}"
            )

        # Align candidate to the next network boundary of its size: if candidate.network_address < current_address,
        # move to the next boundary by incrementing network by one subnet size.
        if int(candidate.network_address) < current_address:
            # increase candidate network address by subnet size until >= current_address
            step = candidate.num_addresses
            base_int = int(candidate.network_address)
            k = math.ceil((current_address - base_int) / step)
            new_network_int = base_int + k * step
            candidate = ipaddress.IPv4Network((new_network_int, prefix), strict=False)
            if int(candidate.broadcast_address) > last_address:
                raise RuntimeError(
                    f"Insufficient address space: cannot align and allocate /{prefix} for {req_hosts} hosts."
                )

        # Assign candidate
        allocations.append((orig_idx, candidate, req_hosts))

        # Move current_address to next address after the allocated subnet
        current_address = int(candidate.broadcast_address) + 1

    # Sort allocations back to original order (optional) — here we return allocations in allocation order
    # Return list of dicts
    results = []
    for i, (orig_idx, subnet, req_hosts) in enumerate(allocations, start=1):
        total_addrs = subnet.num_addresses
        usable = total_addrs - 2 if total_addrs >= 2 else 0
        first_usable = None
        last_usable = None
        if usable > 0:
            first_usable = ipaddress.IPv4Address(int(subnet.network_address) + 1)
            last_usable = ipaddress.IPv4Address(int(subnet.broadcast_address) - 1)
        results.append({
            "subnet_id": i,
            "orig_index": orig_idx,
            "network": str(subnet.network_address),
            "prefix": f"/{subnet.prefixlen}",
            "netmask": str(subnet.netmask),
            "first_usable": str(first_usable) if first_usable else "-",
            "last_usable": str(last_usable) if last_usable else "-",
            "broadcast": str(subnet.broadcast_address),
            "total_addresses": total_addrs,
            "usable_hosts": usable,
            "requested_hosts": req_hosts,
            "cidr": str(subnet.with_prefixlen),
        })
    return results


def print_table(results: List[Dict], base_net: ipaddress.IPv4Network):
    print(f"Base network: {base_net.with_prefixlen}\n")
    fmt = "{:<6} {:<18} {:<6} {:<15} {:<15} {:<15} {:<15} {:<6} {:<6}"
    hdr = fmt.format("ID", "Network/CIDR", "Prefix", "Netmask", "First", "Last", "Broadcast", "Total", "Usable")
    print(hdr)
    print("-" * len(hdr))
    for r in results:
        print(fmt.format(
            r["subnet_id"],
            r["cidr"],
            r["prefix"],
            r["netmask"],
            r["first_usable"],
            r["last_usable"],
            r["broadcast"],
            r["total_addresses"],
            r["usable_hosts"],
        ))
    print()


def write_csv(results: List[Dict], csv_path: str):
    keys = ["subnet_id", "cidr", "prefix", "network", "netmask", "first_usable", "last_usable", "broadcast", "total_addresses", "usable_hosts", "requested_hosts"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in keys})


def parse_hosts_arg(s: str) -> List[int]:
    parts = [p.strip() for p in s.split(",") if p.strip()]
    return [int(p) for p in parts]


def main():
    parser = argparse.ArgumentParser(description="VLSM Subnet Allocator")
    parser.add_argument("--network", "-n", help="Base network in CIDR (e.g., 192.168.0.0/24)")
    parser.add_argument("--hosts", "-H", help="Comma-separated host counts, e.g., 50,20,10,5")
    parser.add_argument("--output", "-o", help="Optional CSV output file path")
    args = parser.parse_args()

    if not args.network:
        base = input("Enter base network (CIDR), e.g. 192.168.0.0/24: ").strip()
    else:
        base = args.network.strip()

    try:
        base_net = ipaddress.IPv4Network(base, strict=True)
    except Exception as e:
        print(f"Invalid base network: {e}")
        return

    if not args.hosts:
        hosts_input = input("Enter required hosts per subnet (comma-separated), e.g. 50,20,10,5: ").strip()
    else:
        hosts_input = args.hosts.strip()

    try:
        requirements = parse_hosts_arg(hosts_input)
    except Exception as e:
        print(f"Invalid hosts list: {e}")
        return

    try:
        results = allocate_vlsm(base_net, requirements)
    except Exception as e:
        print("Allocation error:", e)
        return

    print_table(results, base_net)

    if args.output:
        try:
            write_csv(results, args.output)
            print(f"Wrote results to {args.output}")
        except Exception as e:
            print("Failed to write CSV:", e)


if __name__ == "__main__":
    main()
