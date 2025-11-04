## 03_selective_repeat_arq — Selective Repeat ARQ Simulator

### Overview

This project simulates the **Selective Repeat Automatic Repeat reQuest (ARQ)** protocol, one of the most efficient error-control techniques used in reliable data communication.

It models the transmission of frames between a sender and receiver using a **sliding window**, handling **timeouts**, **retransmissions**, and **out-of-order acknowledgments** under simulated network conditions such as **frame loss** and **reordering**.

---

### Features

* Implements a **Selective Repeat** ARQ protocol simulation.
* Simulates **random frame loss** and **reordering**.
* Uses **multithreading** for asynchronous sending and timeout handling.
* Displays **ACK receptions**, **timeouts**, and **window movement** in real time.
* Configurable simulation parameters for experimentation.

---

### File

* `sr_arq_simulator.py` — Main simulation program.

---

### How It Works

1. The sender transmits multiple frames up to the **window size**.
2. Each frame starts a **timer** upon being sent.
3. Frames can be:

   * **Acknowledged** by the receiver.
   * **Lost** due to simulated channel errors.
   * **Reordered** by artificial transmission delays.
4. If an **ACK** isn’t received before the **timeout**, the frame is retransmitted.
5. The sender’s **window slides** forward once consecutive ACKs are received.

---

### Usage

#### Run the simulation

```bash
python sr_arq_simulator.py
```

---

### Example Output

```
Starting Selective Repeat ARQ simulation...

[SEND] Frame 0 sent.
[SEND] Frame 1 sent.
[SEND] Frame 2 sent.
[SEND] Frame 3 sent.
[LOSS] Frame 2 lost in transit.
[ACK RECEIVED] Frame 0 acknowledged.
[TIMEOUT] Frame 2 timed out. Retransmitting...
[ACK RECEIVED] Frame 1 acknowledged.
[ACK RECEIVED] Frame 3 acknowledged.
[ACK RECEIVED] Frame 2 acknowledged.

All frames transmitted and acknowledged successfully.
```

---

### Configuration

Edit the top of the script to modify parameters:

```python
TOTAL_FRAMES = 10           # Total number of frames to send
WINDOW_SIZE = 4             # Sliding window size
LOSS_PROBABILITY = 0.2      # Probability of frame loss
REORDER_PROBABILITY = 0.2   # Probability of frame reordering
TIMEOUT = 2.0               # Timeout duration (seconds)
DELAY_RANGE = (0.5, 1.5)    # Simulated transmission delay (seconds)
```

Try increasing `LOSS_PROBABILITY` or `WINDOW_SIZE` to see how it affects performance and retransmissions.

---

### Concepts Demonstrated

| Concept                      | Description                                                         |
| ---------------------------- | ------------------------------------------------------------------- |
| **Sliding Window**           | Controls how many frames can be in transit simultaneously.          |
| **Timeout & Retransmission** | Frames not acknowledged in time are resent.                         |
| **Out-of-Order Delivery**    | Frames may arrive out of sequence and still be processed correctly. |
| **Reliability Simulation**   | Demonstrates real-world data link reliability strategies.           |

---

### Requirements

* Python 3.7+
* No external dependencies required.

---

### References

* Tanenbaum, A. S. — *Computer Networks*
* Forouzan, B. — *Data Communications and Networking*
* RFC 3366 — *Selective Repeat Protocol Behavior and Design Considerations*
