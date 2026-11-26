"""In-memory JWT blacklist untuk logout server-side.

ERD tidak memiliki tabel token, sehingga blacklist disimpan di memori proses
(entri otomatis dibuang setelah token kedaluwarsa). Untuk deployment multi-worker,
ganti implementasi ini dengan Redis.
"""
import threading
import time

_lock = threading.Lock()
_blacklist: dict[str, float] = {}  # jti -> exp (unix timestamp)


def _purge(now: float) -> None:
    for jti in [j for j, exp in _blacklist.items() if exp < now]:
        _blacklist.pop(jti, None)


def add(jti: str, exp: float) -> None:
    with _lock:
        _purge(time.time())
        _blacklist[jti] = exp


def contains(jti: str) -> bool:
    with _lock:
        exp = _blacklist.get(jti)
        if exp is None:
            return False
        if exp < time.time():
            _blacklist.pop(jti, None)
            return False
        return True

