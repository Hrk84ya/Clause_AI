import time
from datetime import timedelta

import pytest
from fastapi import HTTPException

from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify_roundtrip(self):
        password = "MySecure123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct_password1")
        assert not verify_password("wrong_password1", hashed)

    def test_different_hashes_for_same_password(self):
        password = "SamePassword1"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # bcrypt uses random salt
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWT:
    def test_encode_decode_roundtrip(self):
        data = {"sub": "user-123", "email": "test@example.com"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"

    def test_expired_token_raises_401(self):
        data = {"sub": "user-123"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401

    def test_invalid_token_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_tampered_token_raises_401(self):
        token = create_access_token({"sub": "user-123"})
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(tampered)
        assert exc_info.value.status_code == 401


class TestRefreshToken:
    def test_creates_raw_and_hash(self):
        raw, hashed = create_refresh_token()
        assert len(raw) > 32
        assert len(hashed) == 64  # SHA-256 hex digest
        assert raw != hashed

    def test_different_tokens_each_call(self):
        raw1, hash1 = create_refresh_token()
        raw2, hash2 = create_refresh_token()
        assert raw1 != raw2
        assert hash1 != hash2
