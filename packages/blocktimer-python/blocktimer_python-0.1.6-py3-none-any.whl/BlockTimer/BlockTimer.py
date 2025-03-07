# -*- encoding: utf-8 -*-
# ! python3

import sys
import time
from contextlib import ContextDecorator
from typing import Any, Dict, List, Optional

import numpy as np
from tabulate import tabulate  # Added for table formatting


class BlockTimeManager:
    """Manages multiple timers and their formats."""

    def __init__(self, window_size=10, buf_size=100000):
        self.timers: Dict[str, "Timer"] = dict()
        self.timer_fmts: Dict[str, Optional[str]] = dict()
        self.window_size = window_size
        self.buf_size = buf_size

    def print_all_timers(self, format_type="table"):
        """Print all timers in a formatted table or as individual lines."""
        if not self.timers:
            print("No timers registered")
            return

        if format_type == "table":
            headers = [
                "Name",
                "Calls",
                "Latest (s)",
                "Window Avg (s)",
                "Avg (s)",
                "Var",
                "Total (s)",
            ]
            data = []

            for name, timer in self.timers.items():
                bt = BlockTimer(name)  # Create temporary BlockTimer to access stats
                data.append(
                    [
                        name,
                        bt.num_calls,
                        f"{bt.latest:.4f}",
                        f"{bt.wavg:.4f}",
                        f"{bt.avg:.4f}",
                        f"{bt.var:.4f}",
                        f"{bt.total:.4f}",
                    ]
                )

            print(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            # Print each timer on its own line
            for name in self.timers:
                print(BlockTimer(name))


# Global BlockTimeManager instance
btm = BlockTimeManager(window_size=100000)


class Timer:
    """Base timer class that handles time measurements."""

    def __init__(self, name, window_size, buf_size=100000):
        self.name = name
        self.buf_size = buf_size
        self.window_size = window_size
        self.init()
        self.num_calls = 0  # Track number of calls

    def init(self):
        """Initialize or reset the timer's state."""
        self.measures_arr = np.empty(
            (0, 2)
        )  # LIFO array of [start_time, end_time] pairs
        self.current_start = None
        self.current_end = None

    def reset(self):
        """Reset the timer to its initial state."""
        self.init()
        self.num_calls = 0

    def tic(self):
        """Start timing."""
        if self.current_start is not None:
            # another tic executed before a toc
            self.toc()
        self.current_start = time.perf_counter()
        self.num_calls += 1

    def toc(self):
        """Stop timing and record the measurement."""
        self.current_end = time.perf_counter()
        self._add_current_measure()

    def _add_current_measure(self):
        """Add the current timing measurement to the measures array."""
        self.measures_arr = np.concatenate(
            [
                np.array([[self.current_start, self.current_end]]),
                self.measures_arr[: self.buf_size],
            ]
        )
        self.current_start = None
        self.current_end = None

    @property
    def avg(self) -> float:
        """Average execution time across all measurements."""
        return np.mean(self.measures_arr[:, 1] - self.measures_arr[:, 0])

    @property
    def wavg(self) -> float:
        """Windowed average execution time (limited to window_size most recent measurements)."""
        return np.mean(
            self.measures_arr[: self.window_size, 1]
            - self.measures_arr[: self.window_size, 0]
        )

    @property
    def max(self) -> float:
        """Maximum execution time."""
        return np.max(self.measures_arr[:, 1] - self.measures_arr[:, 0])

    @property
    def min(self) -> float:
        """Minimum execution time."""
        return np.min(self.measures_arr[:, 1] - self.measures_arr[:, 0])

    @property
    def total(self) -> float:
        """Total execution time across all measurements."""
        return np.sum(self.measures_arr[:, 1] - self.measures_arr[:, 0])

    @property
    def latest(self) -> float:
        """Most recent execution time."""
        return self.measures_arr[0, 1] - self.measures_arr[0, 0]

    @property
    def median(self) -> float:
        """Median execution time."""
        return np.median(self.measures_arr[:, 1] - self.measures_arr[:, 0])

    @property
    def var(self) -> float:
        """Variance in execution times."""
        return np.var(self.measures_arr[:, 1] - self.measures_arr[:, 0])


class BlockTimer(ContextDecorator):
    """Context manager and decorator for timing code blocks."""

    @staticmethod
    def timers():
        """Return a list of all registered timer names."""
        return list(btm.timers.keys())

    @staticmethod
    def print_all(format_type="table"):
        """Print all timers in a formatted table or as individual lines."""
        btm.print_all_timers(format_type)

    def __init__(self, name, fmt=None, window_size=100):
        self.name = name
        if name in btm.timers:
            self.timer = btm.timers[name]
            # restore format
            self.fmt = fmt if fmt is not None else btm.timer_fmts[name]
        else:
            self.timer = Timer(name, btm.window_size, btm.buf_size)
            btm.timers[name] = self.timer
            btm.timer_fmts[name] = fmt
        self.timer.window_size = window_size
        self._default_fmt = "[{name}] num: {num} latest: {latest:.4f} --wind_avg: {wavg:.4f} -- avg: {avg:.4f} --var: {var:.4f} -- total: {total:.4f}"
        if fmt == "default":
            self.fmt = self._default_fmt
        # extend here for new formats
        else:
            self.fmt = None

        self.num_calls = self.timer.num_calls  # Use timer's call count

    def __enter__(self) -> "BlockTimer":  # Fixed return type annotation
        self.tic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # Named parameters for clarity
        self.toc()
        if self.fmt is not None:
            print(str(self))

    def __str__(self) -> str:
        """String representation of the timer."""
        return self.display()

    def reset(self):
        """Reset the timer."""
        self.timer.reset()
        self.num_calls = 0

    def display(self, fmt=None):
        """Format and return timer statistics as a string."""
        if fmt is None:
            if self.fmt is not None:
                fmt = self.fmt
            else:
                fmt = self._default_fmt
        return fmt.format(
            name=self.name,
            num=self.num_calls,
            latest=self.latest,
            wavg=self.wavg,
            avg=self.avg,
            var=self.var,
            total=self.total,
        )

    def tic(self):
        """Start timing."""
        self.timer.tic()
        self.num_calls = self.timer.num_calls  # Update from timer

    def toc(self, display=False):
        """Stop timing and optionally display results."""
        self.timer.toc()
        if display:
            return self.display()

    @property
    def latest(self) -> float:
        return self.timer.latest

    @property
    def avg(self) -> float:
        return self.timer.avg

    @property
    def wavg(self) -> float:
        return self.timer.wavg

    @property
    def max(self) -> float:
        return self.timer.max

    @property
    def min(self) -> float:
        return self.timer.min

    @property
    def total(self) -> float:
        return self.timer.total

    @property
    def median(self) -> float:
        return self.timer.median

    @property
    def var(self) -> float:
        return self.timer.var


if __name__ == "__main__":
    # Example usage as a decorator
    @BlockTimer("fct", "default")
    def fct(value):
        """Example function that sleeps for demonstration."""
        time.sleep(0.5)

    fct(2)

    # Example usage as a context manager
    for i in range(10):
        with BlockTimer("affe", "default"):
            time.sleep(0.1)

    for i in range(1000):
        with BlockTimer("test", None):
            time.sleep(0.001)

    print(BlockTimer("test"))
    BlockTimer("test").tic()
    BlockTimer("t2", "default").tic()
    time.sleep(0.4)
    print(BlockTimer("t2").toc(True))

    time.sleep(0.4)
    print(BlockTimer("test").toc(True))

    # Print all timers in a table format
    print("\nAll Timers:")
    BlockTimer.print_all()
