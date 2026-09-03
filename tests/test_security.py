from app.core.security import hash_password, verify_password


def test_verify_password_accepts_correct_password() -> None:
    plain_password = "correct-horse-test-password"
    password_hash = hash_password(plain_password)

    assert verify_password(plain_password, password_hash) is True


def test_verify_password_rejects_wrong_password() -> None:
    correct_password = "correct-horse-test-password"
    wrong_password = "wrong-test-password"
    password_hash = hash_password(correct_password)

    assert verify_password(wrong_password, password_hash) is False