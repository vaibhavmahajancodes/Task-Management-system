import secrets

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def generate_opaque_token(num_bytes: int = 32) -> str:
    """Cryptographically secure random token used for refresh / reset tokens."""
    return secrets.token_urlsafe(num_bytes)
