"""Direct-assert test for camera_reconnect.py -- no camera hardware, no
pytest, just dependency-injected fakes and plain asserts. This mirrors the
testing style used across the real project: every module gets a
test_*.py that exercises it in isolation, and a single runner script
discovers and runs all of them with one command.
"""
from camera_reconnect import reconnect_camera


class _FakeCap:
    def __init__(self, read_result):
        self._read_result = read_result
        self.released = False

    def read(self):
        return self._read_result

    def release(self):
        self.released = True


def _make_open_camera_fn(behaviors):
    created = []
    behaviors_iter = iter(behaviors)

    def _fn(source):
        behavior = next(behaviors_iter)
        if behavior == "raise":
            raise RuntimeError("camera not available (fake)")
        cap = _FakeCap((True, "frame") if behavior == "ok" else (False, None))
        created.append(cap)
        return cap

    return _fn, created


def test_reconnect_succeeds_on_second_attempt():
    open_camera_fn, created = _make_open_camera_fn(["raise", "ok"])
    sleep_calls = []
    result = reconnect_camera(0, open_camera_fn, sleep_fn=sleep_calls.append,
                               max_attempts=5, backoff_base=1.0)
    assert result is created[0]
    assert sleep_calls == [1.0, 2.0]
    print(">>> PASS: succeeds on second attempt, correct exponential backoff")


def test_reconnect_releases_dead_handle_before_retrying():
    open_camera_fn, created = _make_open_camera_fn(["read_fail", "ok"])
    result = reconnect_camera(0, open_camera_fn, sleep_fn=lambda s: None,
                               max_attempts=5, backoff_base=1.0)
    assert result is created[1]
    assert created[0].released is True
    print(">>> PASS: dead handle released before retry, no leaked handles")


def test_reconnect_exhausts_attempts_returns_none():
    open_camera_fn, created = _make_open_camera_fn(["read_fail", "read_fail", "raise"])
    result = reconnect_camera(0, open_camera_fn, sleep_fn=lambda s: None,
                               max_attempts=3, backoff_base=0.5)
    assert result is None
    assert all(c.released for c in created)
    print(">>> PASS: all attempts exhausted -> None, no abandoned handles")


if __name__ == "__main__":
    test_reconnect_succeeds_on_second_attempt()
    test_reconnect_releases_dead_handle_before_retrying()
    test_reconnect_exhausts_attempts_returns_none()
    print(">>> 3/3 TEST PASS")
