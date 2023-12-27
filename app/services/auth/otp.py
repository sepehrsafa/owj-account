from pyotp import TOTP, random_base32

from app.config import settings

from .encrypt import decrypt, encrypt


def get_otp_hash() -> str:
    return encrypt(random_base32())


async def check_otp(encrypted_hash: str, code: str) -> bool:
    otp_hash = await decrypt(encrypted_hash)
    totp = TOTP(s=otp_hash, digits=settings.otp.digits, interval=settings.otp.interval)
    return totp.verify(code)


async def get_otp(encrypted_hash) -> str:
    otp_hash = await decrypt(encrypted_hash)
    totp = TOTP(s=otp_hash, digits=settings.otp.digits, interval=settings.otp.interval)
    return totp.now()
