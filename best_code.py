#!/usr/bin/env python3
"""
best_code.py – A minimal implementation of Conway’s Game of Life.

Features
--------
* `Grid` class:
    •  Arbitrary grid size  
    •  Display to terminal using “█” for live cells  
    •  `step()` to advance one generation  
    •  `count_live_neighbors()` helper
* Built-in test pattern (a glider) so you can see motion.
* Runs as a script and prints 20 generations with a short delay.

Run
---
$ python best_code.py
"""

from __future__ import annotations

import os
import time
from typing import List


class Grid:
    """Finite, non-wrapping Game-of-Life grid."""

    def __init__(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols
        self.cells: List[List[bool]] = [[False] * cols for _ in range(rows)]

    # ─────────────────────────────── helpers ──────────────────────────────── #

    def set_alive(self, row: int, col: int, alive: bool = True) -> None:
        """Set a single cell’s state (silently ignores out-of-bounds)."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.cells[row][col] = alive

    def count_live_neighbors(self, row: int, col: int) -> int:
        """Return the number of live neighbors around (row, col)."""
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols and self.cells[r][c]:
                    count += 1
        return count

    # ───────────────────────────── core methods ───────────────────────────── #

    def step(self) -> None:
        """Advance the grid by one generation according to the four rules."""
        new_state = [[False] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                live_neighbors = self.count_live_neighbors(r, c)
                if self.cells[r][c]:  # currently alive
                    new_state[r][c] = live_neighbors in (2, 3)
                else:  # currently dead
                    new_state[r][c] = live_neighbors == 3
        self.cells = new_state

    def display(self) -> None:
        """Print the grid to the terminal."""
        lines = ("".join("█" if cell else " " for cell in row) for row in self.cells)
        print("\n".join(lines))


# ─────────────────────────── test-pattern helpers ────────────────────────── #


def add_glider(grid: Grid, top: int = 0, left: int = 0) -> None:
    """Insert a classic glider with its head at (top, left)."""
    pattern = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    for dr, dc in pattern:
        grid.set_alive(top + dr, left + dc)


def add_blinker(grid: Grid, row: int, col: int) -> None:
    """Insert a horizontal blinker centered at (row, col)."""
    for dc in (-1, 0, 1):
        grid.set_alive(row, col + dc)


# ────────────────────────────────── main ─────────────────────────────────── #


def main() -> None:
    rows, cols = 20, 20
    g = Grid(rows, cols)

    # Choose ONE of the patterns below (glider by default).
    add_glider(g, 1, 1)
    # add_blinker(g, 10, 10)

    generations = 20
    delay_sec = 0.25

    for gen in range(generations):
        # Clear screen for nicer animation.
        os.system("cls" if os.name == "nt" else "clear")
        print(f"Generation {gen}")
        g.display()
        g.step()
        time.sleep(delay_sec)


if __name__ == "__main__":
    main()