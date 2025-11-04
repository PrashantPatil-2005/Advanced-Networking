"""
Project: Distance Vector Routing Convergence
Author: Pra P.
Description:
    This program simulates the Distance Vector Routing algorithm (similar to RIP).
    Each node maintains a routing table and periodically exchanges updates with neighbors
    until all nodes reach convergence (stable shortest paths).

Features:
    - Simulates distance vector updates between nodes
    - Detects and displays count-to-infinity conditions
    - Demonstrates convergence detection
    - Customizable network topology

Usage:
    python distance_vector_simulator.py
"""

import time
import copy


INFINITY = 9999


class Node:
    """Represents a network node participating in Distance Vector routing."""

    def __init__(self, name, neighbors):
        """
        name: str - node identifier (e.g., 'A')
        neighbors: dict - {neighbor_name: cost}
        """
        self.name = name
        self.neighbors = neighbors
        self.distance_vector = {dest: INFINITY for dest in neighbors}
        self.distance_vector[name] = 0
        self.routing_table = {dest: dest for dest in neighbors}
        self.routing_table[name] = name

    def __str__(self):
        table = "\n".join(
            f"  Dest: {dest}, Cost: {cost}, Next Hop: {self.routing_table.get(dest, '-')}"
            for dest, cost in self.distance_vector.items()
        )
        return f"\nRouting table for Node {self.name}:\n{table}\n"

    def send_update(self):
        """Send current distance vector to all neighbors."""
        return copy.deepcopy(self.distance_vector)

    def receive_update(self, neighbor, neighbor_vector, link_cost):
        """Update own table using information from a neighbor."""
        updated = False
        for dest, neighbor_cost in neighbor_vector.items():
            if dest not in self.distance_vector:
                self.distance_vector[dest] = INFINITY
                self.routing_table[dest] = None

            new_cost = link_cost + neighbor_cost
            if new_cost < self.distance_vector[dest]:
                self.distance_vector[dest] = new_cost
                self.routing_table[dest] = neighbor
                updated = True

            # Detect count-to-infinity scenario
            if self.distance_vector[dest] > 50:  # arbitrary large value
                self.distance_vector[dest] = INFINITY
                self.routing_table[dest] = None

        return updated


class Network:
    """Simulates a network running the Distance Vector Routing algorithm."""

    def __init__(self, topology):
        """
        topology: dict - {
            'A': {'B': 2, 'C': 5},
            'B': {'A': 2, 'C': 1},
            'C': {'A': 5, 'B': 1}
        }
        """
        self.nodes = {name: Node(name, neighbors) for name, neighbors in topology.items()}

    def run_until_convergence(self, max_rounds=20):
        print("Starting Distance Vector Routing simulation...\n")

        for round_no in range(1, max_rounds + 1):
            print(f"--- Round {round_no} ---")
            updated = False

            # Prepare all updates
            updates = {name: node.send_update() for name, node in self.nodes.items()}

            # Exchange distance vectors
            for node_name, node in self.nodes.items():
                for neighbor, cost in node.neighbors.items():
                    if neighbor in self.nodes:
                        changed = node.receive_update(neighbor, updates[neighbor], cost)
                        updated = updated or changed

            # Print current routing tables
            for node in self.nodes.values():
                print(node)

            if not updated:
                print(f"Convergence achieved after {round_no} rounds.\n")
                break
            else:
                time.sleep(1)
        else:
            print("Reached maximum rounds without full convergence.\n")


def main():
    # Define the network topology
    topology = {
        'A': {'B': 2, 'C': 5},
        'B': {'A': 2, 'C': 1, 'D': 3},
        'C': {'A': 5, 'B': 1, 'D': 2},
        'D': {'B': 3, 'C': 2}
    }

    network = Network(topology)
    network.run_until_convergence()


if __name__ == "__main__":
    main()
