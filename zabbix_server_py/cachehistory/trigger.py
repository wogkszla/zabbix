"""Simplified trigger evaluation routines.

This module is a high-level rewrite of parts of ``trigger_eval.c``.  Only a
very small subset of functionality is provided for unit testing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .cache import HistoryCache


@dataclass
class Trigger:
    """Representation of a trigger expression."""

    triggerid: int
    expression: str

    def evaluate(self, cache: HistoryCache) -> bool:
        """Evaluate the trigger expression using *cache*.

        The expression is executed as a Python expression with ``cache`` in the
        local namespace.  This roughly mirrors the evaluation performed in
        ``evaluate_item_functions`` from ``trigger_eval.c`` but without the
        complex parsing and error handling.
        """

        try:
            return bool(eval(self.expression, {}, {"cache": cache}))
        except Exception:
            return False
