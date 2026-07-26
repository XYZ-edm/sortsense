"""Illustrative version of the camera-reconnection logic used to harden the
main capture loop for unattended operation.

Design goals this demonstrates:
  - transient frame-read failures should trigger a bounded, backed-off retry
    of the *connection*, not an immediate crash of a process meant to run
    unattended for hours;
  - every intermediate "opened but not actually reading frames" handle must
    be released, never silently abandoned;
  - the function is fully unit-testable without a real camera, by injecting
    the "open camera" and "sleep" functions.
"""
import time


def reconnect_camera(source, open_camera_fn, sleep_fn=time.sleep,
                      max_attempts=5, backoff_base=1.0):
    """Attempt to reopen a video source with exponential backoff.

    Returns an opened, verified-readable capture handle, or None if all
    attempts are exhausted.
    """
    for attempt in range(1, max_attempts + 1):
        backoff = backoff_base * (2 ** (attempt - 1))
        sleep_fn(backoff)
        try:
            candidate = open_camera_fn(source)
        except RuntimeError:
            continue

        ok, _ = candidate.read()
        if ok:
            return candidate

        # Opened but not actually delivering frames -- don't leak the handle.
        candidate.release()

    return None
