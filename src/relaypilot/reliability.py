from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class ReconciledResult:
    value: T | None
    attempts: int
    recovered_after_timeout: bool = False


def retry_after_reconciliation(
    attempt: Callable[[], T],
    completion_check: Callable[[], T | None],
    *,
    max_attempts: int = 2,
) -> ReconciledResult[T]:
    """Never blindly repeat an uncertain action: inspect outcome before a bounded retry."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least one")
    for number in range(1, max_attempts + 1):
        try:
            return ReconciledResult(attempt(), number)
        except TimeoutError:
            prior_outcome = completion_check()
            if prior_outcome is not None:
                return ReconciledResult(prior_outcome, number, recovered_after_timeout=True)
            if number == max_attempts:
                raise
    raise AssertionError("unreachable")
