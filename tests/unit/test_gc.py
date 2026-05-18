from src.gc.safety_checks import is_tombstone_safe

def test_safe_when_all_covered():
    assert is_tombstone_safe('a', 5, {'a': {'a':5}, 'b': {'a':5}})

def test_unsafe_when_peer_behind():
    assert not is_tombstone_safe('a', 5, {'a': {'a':5}, 'b': {'a':3}})
