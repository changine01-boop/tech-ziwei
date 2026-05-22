"""Unit tests for auth service — no database required."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tech_ziwei.services.auth import (
    hash_password, verify_password, create_access_token, decode_token
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("secret123")
        assert hashed != "secret123"

    def test_verify_correct_password(self):
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_same_password_different_hashes(self):
        h1 = hash_password("pw")
        h2 = hash_password("pw")
        assert h1 != h2  # bcrypt salts each hash


class TestJWT:
    def test_encode_decode_roundtrip(self):
        token = create_access_token("user-123")
        assert decode_token(token) == "user-123"

    def test_invalid_token_raises(self):
        from jose import JWTError
        with pytest.raises(JWTError):
            decode_token("not.a.valid.token")

    def test_tampered_token_raises(self):
        from jose import JWTError
        token = create_access_token("user-abc")
        tampered = token[:-4] + "xxxx"
        with pytest.raises(JWTError):
            decode_token(tampered)
