from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
import jwt
import pytest


def test_verify_password_accepts_correct_password() -> None:
    plain_password = "correct-horse-test-password"
    password_hash = hash_password(plain_password)

    assert verify_password(plain_password, password_hash) is True


def test_verify_password_rejects_wrong_password() -> None:
    correct_password = "correct-horse-test-password"
    wrong_password = "wrong-test-password"
    password_hash = hash_password(correct_password)

    assert verify_password(wrong_password, password_hash) is False

def test_access_token_preserves_subject() -> None:
    token = create_access_token(subject="test-admin")

    payload = decode_access_token(token)

    assert payload["sub"] == "test-admin"

def test_decode_access_token_rejects_expired_token() -> None:
    token = create_access_token(
        subject="test-admin",
        expires_minutes=-1,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)