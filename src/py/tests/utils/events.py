"""Test utilities for event handling."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

# Wait budget for predicate polling. Listener handlers do real DB work
# (open session, look up user, create token, send email), which can be slow
# on CI, so condition-based waits get a more generous default than the
# legacy fixed sleep.
DEFAULT_CONDITION_MAX_WAIT = 5.0
DEFAULT_SLEEP_MAX_WAIT = 1.0


async def wait_for_events(
    max_wait: float | None = None,
    interval: float = 0.1,
    condition: Callable[[], bool] | None = None,
) -> None:
    """Wait for async event listeners to complete.

    Event listeners run as fire-and-forget tasks with no completion signal,
    so a fixed sleep alone can never guarantee they are done. When a
    ``condition`` is provided, this helper polls it instead and returns as
    soon as it becomes True — making the wait deterministic.

    Args:
        max_wait: Maximum time to wait in seconds. ``None`` (default) uses
            5.0s when ``condition`` is given, or 1.0s otherwise (the
            historical fixed-sleep behavior).
        interval: Time between condition checks in seconds.
        condition: Optional predicate polled until it returns True. If it
            never does within ``max_wait``, an ``AssertionError`` is raised
            naming the condition's source so failures are actionable.

    Raises:
        AssertionError: If ``condition`` is given and does not return True
            within ``max_wait``.
    """
    if condition is None:
        budget = DEFAULT_SLEEP_MAX_WAIT if max_wait is None else max_wait
        elapsed = 0.0
        while elapsed < budget:
            await asyncio.sleep(interval)
            elapsed += interval
        return

    budget = DEFAULT_CONDITION_MAX_WAIT if max_wait is None else max_wait
    elapsed = 0.0
    while elapsed < budget:
        if condition():
            return
        await asyncio.sleep(interval)
        elapsed += interval

    if not condition():
        msg = f"Timed out after {budget}s waiting for condition: {condition!r}"
        raise AssertionError(msg)


def expect_outbox_count(count: int, backend: Any = None) -> Callable[[], bool]:
    """Build a condition asserting that the email outbox holds ``count`` messages.

    Args:
        count: Expected number of messages in the outbox.
        backend: Email backend to inspect; defaults to
            :class:`litestar_email.backends.memory.InMemoryBackend`.

    Returns:
        A zero-argument predicate suitable for ``wait_for_events(condition=...)``.
        Uses ``>=`` so tests that clear between requests stay tolerant of a
        late leftover message from a previous wait.
    """
    if backend is None:
        from litestar_email import InMemoryBackend

        backend = InMemoryBackend

    return lambda: len(backend.outbox) >= count
