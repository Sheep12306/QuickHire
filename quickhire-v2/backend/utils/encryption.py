import os

ENCRYPTED_PREFIX = "enc:"

_fernet = None


def _get_fernet():
    global _fernet
    if _fernet is None:
        from cryptography.fernet import Fernet
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise RuntimeError("ENCRYPTION_KEY not configured")
        _fernet = Fernet(key.encode())
    return _fernet


def encrypt(plaintext: str) -> str:
    if not plaintext:
        return plaintext
    return ENCRYPTED_PREFIX + _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(value: str) -> str:
    if not value:
        return value
    if value.startswith(ENCRYPTED_PREFIX):
        return _get_fernet().decrypt(value[len(ENCRYPTED_PREFIX):].encode()).decode()
    return value


def mask_key(key: str) -> str:
    """Return masked key like sk-abc...xyz"""
    if not key:
        return ""
    if len(key) <= 8:
        return "***"
    return key[:5] + "..." + key[-4:]
