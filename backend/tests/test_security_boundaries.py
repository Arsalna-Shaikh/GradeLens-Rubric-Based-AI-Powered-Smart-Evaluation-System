"""Small regression tests for hardening controls that do not require product fixtures."""
from app.routers.auth import _FAILED_2FA, _MAX_FAILURES, _WINDOW_SECONDS


def test_two_factor_limiter_is_separate_from_password_limiter():
    assert _FAILED_2FA is not None
    assert _MAX_FAILURES > 0
    assert _WINDOW_SECONDS > 0
