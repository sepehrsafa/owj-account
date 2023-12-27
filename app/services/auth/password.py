import uuid
from datetime import datetime, timedelta

import bcrypt
import jwt
import pyotp
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from tortoise import fields, models

from app.config import settings


async def hmac_hash_password(password: str) -> bytes:
    hmac_key = hmac.HMAC(
        settings.password_hash_secret, hashes.SHA256(), backend=default_backend()
    )
    hmac_key.update(password.encode("utf-8"))
    return hmac_key.finalize()


async def hash_password(password: str) -> str:
    # Hash the password with HMAC
    hmac_hash = await hmac_hash_password(password)

    # Hash the HMAC hash with bcrypt
    hashed = bcrypt.hashpw(hmac_hash, bcrypt.gensalt())
    return hashed.decode("utf-8")


async def check_password(hashed_password: str, password: str) -> bool:
    # Hash the password with HMAC
    hmac_hash = await hmac_hash_password(password)

    # Use bcrypt's checkpw for verification
    return bcrypt.checkpw(hmac_hash, hashed_password.encode("utf-8"))
