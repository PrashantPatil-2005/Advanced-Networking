
# 04_distance_vector_routing — Distance Vector Routing Convergence

### Overview

This project simulates the **Distance Vector Routing Algorithm**, similar to the **Routing Information Protocol (RIP)**.
Each node in the network maintains a routing table and periodically exchanges its **distance vector** with its neighbors.
The process continues until all nodes reach **convergence**, meaning no further routing updates occur.

The simulation also includes detection of **count-to-infinity** and **routing loop** conditions, providing a practical demonstration of how routing protocols stabilize in distributed networks.

---

### Features

* Simulates **Distance Vector (DV)** routing behavior among multiple nodes.
* **Periodic vector exchanges** between neighboring nodes.
* **Convergence detection** — simulation stops once all routing tables stabilize.
* **Count-to-infinity** handling to avoid infinite routing loops.
* Simple and extensible **Python-based network topology model**.

---

### File

* `distance_vector_simulator.py` — Main simulation program.

---

### How It Works

1. Each node starts with direct link costs to its neighbors.
2. During each round:

   * Every node shares its current **distance vector** (routing table) with its neighbors.
   * Nodes update their tables using the **Bellman–Ford** formula:

     ```
     D(X, Y) = min{ cost(X, N) + D(N, Y) for all neighbors N }
     ```
3. If any node updates its table, another round is triggered.
4. When no tables change between rounds, the network is said to have **converged**.

---

### Usage

Run the simulator using:

```bash
python distance_vector_simulator.py
```

---

### Example Output

```
Starting Distance Vector Routing simulation...

--- Round 1 ---
Routing table for Node A:
  Dest: B, Cost: 2, Next Hop: B
  Dest: C, Cost: 5, Next Hop: C
  Dest: A, Cost: 0, Next Hop: A

Routing table for Node B:
  Dest: A, Cost: 2, Next Hop: A
  Dest: C, Cost: 1, Next Hop: C
  Dest: D, Cost: 3, Next Hop: D
  Dest: B, Cost: 0, Next Hop: B

...

Convergence achieved after 4 rounds.
```

---

### Configuration

You can modify the **network topology** in the script’s `main()` function:

```python
topology = {
    'A': {'B': 2, 'C': 5},
    'B': {'A': 2, 'C': 1, 'D': 3},
    'C': {'A': 5, 'B': 1, 'D': 2},
    'D': {'B': 3, 'C': 2}
}
```

To experiment:

* Add or remove links
* Change link costs
* Increase `max_rounds` to observe non-converging or unstable cases

---

### Concepts Demonstrated

| Concept                     | Description                                                             |
| --------------------------- | ----------------------------------------------------------------------- |
| **Distance Vector Routing** | Each router advertises its known paths to neighbors periodically.       |
| **Bellman–Ford Algorithm**  | Used to compute the shortest paths iteratively.                         |
| **Convergence**             | The point at which all routers agree on the shortest paths.             |
| **Count-to-Infinity**       | Demonstrates how bad routes can propagate endlessly without prevention. |

---

### Requirements

* Python 3.7+
* No external dependencies required.

---

### References

* Tanenbaum, A. S. — *Computer Networks*
* Forouzan, B. — *Data Communications and Networking*
* RFC 2453 — *Routing Information Protocol (RIP)*

