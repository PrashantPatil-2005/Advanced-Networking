## 05_ospf_link_state — OSPF Link-State Routing Simulator

### Overview

This project simulates the **Open Shortest Path First (OSPF)** link-state routing protocol.
Each router floods its **Link-State Advertisements (LSAs)** to the entire network, constructs a **topology database**, and computes the **shortest paths** to all other routers using **Dijkstra’s algorithm**.

The simulation continues until all routers have identical topology databases — this is known as **convergence**.

---

### Features

* Simulates **link-state advertisement flooding** between routers.
* **Global topology database** synchronization across routers.
* **Dijkstra’s shortest path algorithm** for route computation.
* **Convergence detection** — identifies when all routers agree on network state.
* Outputs **routing tables** for each router after convergence.
* Fully self-contained and easy to extend for experiments.

---

### File

* `ospf_link_state_simulator.py` — Main simulation script.

---

### How It Works

1. Each router knows only its **direct neighbors** and link costs.
2. Routers **flood** their local LSAs to every other router in the network.
3. As LSAs propagate, all routers build a **complete topology view**.
4. Once all routers have the same topology, they **compute shortest paths** using **Dijkstra’s algorithm**.
5. Each router prints its final **routing table** with destination, next hop, and total cost.

---

### Usage

Run the simulation with:

```bash
python ospf_link_state_simulator.py
```

---

### Example Output

```
Starting OSPF Link-State Routing Simulation...

--- Round 1 ---
--- Round 2 ---
Convergence achieved.

Routing Table for Router A:
Destination | Next Hop | Cost
---------------------------------
B            | B        | 2
C            | B        | 5
D            | B        | 3
E            | D        | 6

Routing Table for Router B:
Destination | Next Hop | Cost
---------------------------------
A            | A        | 2
C            | C        | 3
D            | D        | 1
E            | D        | 4
...
```

---

### Configuration

You can customize the **network topology** in the `main()` function:

```python
topology = {
    'A': {'B': 2, 'C': 5},
    'B': {'A': 2, 'C': 3, 'D': 1},
    'C': {'A': 5, 'B': 3, 'D': 2},
    'D': {'B': 1, 'C': 2, 'E': 3},
    'E': {'D': 3}
}
```

Each key represents a router, and the nested dictionary defines **neighbor: cost** pairs.

Try modifying the graph — add routers, adjust costs, or remove links — to observe different convergence behaviors.

---

### Concepts Demonstrated

| Concept                  | Description                                                         |
| ------------------------ | ------------------------------------------------------------------- |
| **Link-State Routing**   | Each router advertises its directly connected links.                |
| **Flooding Mechanism**   | LSAs are propagated to all routers in the network.                  |
| **Topology Database**    | Every router builds a full view of the network.                     |
| **Dijkstra’s Algorithm** | Used to compute the shortest paths from source to all destinations. |
| **Convergence**          | Achieved when all routers share identical topology information.     |

---

### Requirements

* Python 3.7+
* No external dependencies required.

---

### References

* Tanenbaum, A. S. — *Computer Networks*
* Forouzan, B. — *Data Communications and Networking*
* RFC 2328 — *OSPF Version 2 (Link-State Routing Protocol)*

