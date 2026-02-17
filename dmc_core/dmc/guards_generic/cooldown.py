"""Cooldown guard: fail when now_ms < cooldown_until_ms."""


def cooldown_guard(
    cooldown_until_ms: int | None,
    now_ms: int,
) -> tuple[bool, str]:
    """Pass if cooldown_until_ms is None or now_ms >= cooldown_until_ms."""
    if cooldown_until_ms is not None and now_ms < cooldown_until_ms:
        return False, "cooldown_active"
    return True, ""
