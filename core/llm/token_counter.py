"""Token counting placeholder.

Anthropic tokenizer APIs have changed over time; the kernel routes all counting
through this module so provider-specific changes do not leak into agents.
"""

from __future__ import annotations


def estimate_tokens(text: str) -> int:
    """Return a conservative rough token estimate for planning budgets."""

    return max(1, len(text) // 4)
