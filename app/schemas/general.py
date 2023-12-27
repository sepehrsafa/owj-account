import re
from typing import List, Optional, Union

from pydantic import BaseConfig, BaseModel, Field, ValidationError, validator

from owjcommon.exceptions import exception_codes


class Detail(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class ValidationErrorDetail(BaseModel):
    id: str = "E1001"
    message: str = exception_codes["E1001"]
    detail: List[Detail]


class ValidationErrorResponse(BaseModel):
    success: bool = False
    error: ValidationErrorDetail


class ErrorDetail(BaseModel):
    id: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class Response(BaseModel):
    success: bool = True


class Password(BaseModel):
    password: str

    @validator("password", pre=True, always=True)
    def validate_password(cls, value):
        # Check for minimum length
        if len(value) < 8:
            raise ValueError("Password too short")

        # Ensure password contains at least one number
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number")

        # Ensure password contains at least one uppercase letter
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        # Ensure password contains at least one lowercase letter
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")

        return value
