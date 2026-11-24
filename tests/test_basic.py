"""Minimal smoke tests - not comprehensive. Plenty of room for Remy to add more
if asked to 'add tests for this module'."""
import auth


def test_password_hash_roundtrip():
    h = auth.hash_password("correct horse battery staple")
    assert auth.verify_password("correct horse battery staple", h)
    assert not auth.verify_password("wrong password", h)
