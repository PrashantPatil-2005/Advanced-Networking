"""
Project: Selective Repeat ARQ Simulator
Author: Pra P.
Description:
    This Python program simulates the Selective Repeat (SR) ARQ protocol.
    It models reliable data transmission using a sliding window,
    timeouts, retransmissions, and random frame loss or reordering.

Usage:
    python sr_arq_simulator.py
"""

import random
import time
import threading

# ---------------- CONFIGURATION ----------------
TOTAL_FRAMES = 10           # Total number of frames to send
WINDOW_SIZE = 4             # Sender window size
LOSS_PROBABILITY = 0.2      # Probability of frame loss
REORDER_PROBABILITY = 0.2   # Probability of frame reordering
TIMEOUT = 2.0               # Seconds before timeout retransmission
DELAY_RANGE = (0.5, 1.5)    # Random transmission delay per frame
# ------------------------------------------------


class Frame:
    """Represents a single frame."""
    def __init__(self, seq_num, data):
        self.seq_num = seq_num
        self.data = data


class SelectiveRepeatARQ:
    """Simulates the Selective Repeat ARQ protocol."""

    def __init__(self, total_frames, window_size):
        self.total_frames = total_frames
        self.window_size = window_size
        self.base = 0
        self.next_seq_num = 0
        self.ack_received = [False] * total_frames
        self.lock = threading.Lock()

    def send_frame(self, frame):
        """Simulate sending a frame with possible loss or reordering."""
        delay = random.uniform(*DELAY_RANGE)

        # Randomly decide if frame is lost
        if random.random() < LOSS_PROBABILITY:
            print(f"[LOSS] Frame {frame.seq_num} lost in transit.")
            return

        # Simulate random delay and potential reordering
        if random.random() < REORDER_PROBABILITY:
            delay += random.uniform(1.0, 2.0)
            print(f"[REORDER] Frame {frame.seq_num} reordered (delayed).")

        time.sleep(delay)
        self.receive_ack(frame.seq_num)

    def start_timer(self, seq_num):
        """Start a timer for a frame; retransmit if timeout occurs."""
        def timer_thread():
            time.sleep(TIMEOUT)
            with self.lock:
                if not self.ack_received[seq_num]:
                    print(f"[TIMEOUT] Frame {seq_num} timed out. Retransmitting...")
                    threading.Thread(target=self.send_frame, args=(Frame(seq_num, f"Data{seq_num}"),)).start()
        threading.Thread(target=timer_thread, daemon=True).start()

    def receive_ack(self, seq_num):
        """Simulate acknowledgment reception."""
        with self.lock:
            if not self.ack_received[seq_num]:
                self.ack_received[seq_num] = True
                print(f"[ACK RECEIVED] Frame {seq_num} acknowledged.")

                # Slide window if base frame was acknowledged
                while self.base < self.total_frames and self.ack_received[self.base]:
                    self.base += 1

    def run(self):
        """Run the simulation."""
        print("Starting Selective Repeat ARQ simulation...\n")

        while self.base < self.total_frames:
            with self.lock:
                # Send frames within the window
                while self.next_seq_num < self.base + self.window_size and self.next_seq_num < self.total_frames:
                    frame = Frame(self.next_seq_num, f"Data{self.next_seq_num}")
                    print(f"[SEND] Frame {frame.seq_num} sent.")
                    threading.Thread(target=self.send_frame, args=(frame,)).start()
                    self.start_timer(frame.seq_num)
                    self.next_seq_num += 1

            time.sleep(0.5)  # Allow background threads to operate

        print("\nAll frames transmitted and acknowledged successfully.")


def main():
    arq = SelectiveRepeatARQ(TOTAL_FRAMES, WINDOW_SIZE)
    arq.run()


if __name__ == "__main__":
    main()
