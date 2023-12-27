import base64

from cryptography.fernet import Fernet

from app.config import settings


def encrypt(secret: str) -> str:
    cipher_suite = Fernet(settings.encryption_key)
    encrypted_secret = cipher_suite.encrypt(secret.encode("utf-8"))
    # Convert bytes to Base64 encoded string
    encrypted_string = base64.urlsafe_b64encode(encrypted_secret).decode("utf-8")
    return encrypted_string


async def decrypt(encrypted_string: str) -> str:
    cipher_suite = Fernet(settings.encryption_key)
    # Convert Base64 encoded string back to bytes
    encrypted_secret_bytes = base64.urlsafe_b64decode(encrypted_string)
    decrypted_secret = cipher_suite.decrypt(encrypted_secret_bytes).decode("utf-8")
    return decrypted_secret
