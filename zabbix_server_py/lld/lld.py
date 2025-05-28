"""Simplified functions from ``lld.c``.

Original functions include::
    lld_item_compare_func
    lld_item_link_compare_func
    lld_item_full_compare_func
    lld_item_prototype_compare_func
    lld_process_discovery_rule
"""

from __future__ import annotations


def parse_rule(rule: str) -> dict:
    """Parse a discovery rule specification.

    The original C code parses complex rule structures.  The Python
    variant only supports ``key=value`` pairs separated by ``;``.
    Numeric values are converted to integers.
    """
    result: dict[str, object] = {}
    for part in rule.split(";"):
        if not part:
            continue
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        if value.isdigit():
            result[key] = int(value)
        else:
            result[key] = value
    return result


def discover_items(rule: dict) -> list[str]:
    """Return item names discovered from *rule*.

    This merely splits the ``items`` field by commas.  Real discovery
    would parse item prototypes and query hosts.
    """
    items = rule.get("items")
    if not items:
        return []
    if isinstance(items, list):
        return [str(i) for i in items]
    return [p for p in str(items).split(",") if p]
