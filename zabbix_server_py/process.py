"""Process management helpers.

Functions here are modeled after zbx_child_fork() and related code in
src/libs/zbxthreads/threads.c.
"""
from __future__ import annotations
import multiprocessing as mp
from multiprocessing import Process
from typing import Callable


def start_master() -> None:
    """Start a demo worker process.

    The real server forks multiple workers. Here we spawn one process
    using Python's multiprocessing API.
    """
    p = Process(target=_worker)
    p.start()
    p.join()


def _worker() -> None:
    print("worker started")
