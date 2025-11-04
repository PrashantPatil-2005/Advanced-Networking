"""
05_ospf_link_state_simulator.py
-----------------------------------
A simulation of the OSPF (Open Shortest Path First) link-state routing protocol.

Each router:
- Floods its link-state information (neighbor costs) to the network.
- Builds a global topology database.
- Computes shortest paths using Dijkstra's algorithm.

This simulation models convergence when all routers have identical topology databases.
"""

import heapq
import copy
import time

class Router:
    def __init__(self, name, neighbors):
        self.name = name
        self.neighbors = neighbors  # {neighbor: cost}
        self.topology_db = {name: neighbors.copy()}  # initial LSA info
        self.routing_table = {}

    def flood_lsa(self, network):
        """Flood link-state information to all routers."""
        for router in network.values():
            if router.name != self.name:
                router.receive_lsa(self.name, self.neighbors)

    def receive_lsa(self, router_name, lsa):
        """Update topology database when receiving an LSA."""
        if router_name not in self.topology_db or self.topology_db[router_name] != lsa:
            self.topology_db[router_name] = lsa.copy()

    def compute_routing_table(self):
        """Run Dijkstra's algorithm on the topology database."""
        graph = self.topology_db
        unvisited = []
        distances = {node: float('inf') for node in graph}
        previous = {node: None for node in graph}

        distances[self.name] = 0
        heapq.heappush(unvisited, (0, self.name))

        while unvisited:
            current_dist, current_node = heapq.heappop(unvisited)
            if current_dist > distances[current_node]:
                continue

            for neighbor, cost in graph.get(current_node, {}).items():
                distance = current_dist + cost
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(unvisited, (distance, neighbor))

        # Build routing table
        routing_table = {}
        for dest in distances:
            if dest == self.name:
                continue
            next_hop = dest
            while previous[next_hop] != self.name and previous[next_hop] is not None:
                next_hop = previous[next_hop]
            routing_table[dest] = (next_hop, distances[dest])
        self.routing_table = routing_table

    def print_routing_table(self):
        print(f"\nRouting Table for Router {self.name}:")
        print("Destination | Next Hop | Cost")
        print("---------------------------------")
        for dest, (next_hop, cost) in sorted(self.routing_table.items()):
            print(f"{dest:^11} | {next_hop:^8} | {cost:^4}")
        print()


def simulate_ospf(network_topology):
    """Simulate the flooding and routing computation of OSPF."""
    routers = {name: Router(name, neighbors) for name, neighbors in network_topology.items()}

    print("Starting OSPF Link-State Routing Simulation...\n")

    rounds = 0
    while True:
        rounds += 1
        print(f"--- Round {rounds} ---")

        # Step 1: Each router floods LSAs
        for router in routers.values():
            router.flood_lsa(routers)

        # Step 2: Check for convergence
        all_dbs = [r.topology_db for r in routers.values()]
        if all(all_dbs[0] == db for db in all_dbs):
            print("Convergence achieved.")
            break

        time.sleep(0.5)

    # Step 3: Compute routing tables
    for router in routers.values():
        router.compute_routing_table()
        router.print_routing_table()


def main():
    # Example network topology (graph)
    topology = {
        'A': {'B': 2, 'C': 5},
        'B': {'A': 2, 'C': 3, 'D': 1},
        'C': {'A': 5, 'B': 3, 'D': 2},
        'D': {'B': 1, 'C': 2, 'E': 3},
        'E': {'D': 3}
    }

    simulate_ospf(topology)


if __name__ == "__main__":
    main()
