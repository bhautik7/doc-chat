from app.authentication.hashing import hash_password, verify_password


def test_hash_password_does_not_return_plaintext():
    hashed = hash_password("testpass123")

    assert hashed != "testpass123"
    assert hashed.startswith("$2b$")


def test_hash_password_salts_each_hash():
    assert hash_password("testpass123") != hash_password("testpass123")


def test_verify_password_accepts_matching_password():
    assert verify_password("testpass123", hash_password("testpass123")) is True


def test_verify_password_rejects_wrong_password():
    assert verify_password("wrongpass", hash_password("testpass123")) is False
