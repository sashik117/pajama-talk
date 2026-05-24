from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.languages import normalize_language_code, normalize_native_language_code


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(default="Dreamer", min_length=1, max_length=80)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    learning_vibe: str
    active_language_code: str
    native_language_code: str
    daily_vibe_minutes: int
    ai_tone: str


class ProfileUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=80)
    learning_vibe: str | None = Field(default=None, min_length=1, max_length=24)
    active_language_code: str | None = None
    native_language_code: str | None = None
    daily_vibe_minutes: int | None = Field(default=None, ge=1, le=180)
    ai_tone: str | None = Field(default=None, min_length=1, max_length=80)

    @field_validator("active_language_code")
    @classmethod
    def validate_active_language(cls, value: str | None) -> str | None:
        return normalize_language_code(value) if value is not None else None

    @field_validator("native_language_code")
    @classmethod
    def validate_native_language(cls, value: str | None) -> str | None:
        return normalize_native_language_code(value) if value is not None else None

    @field_validator("learning_vibe")
    @classmethod
    def validate_learning_vibe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        allowed = {"Chill", "Normal", "Hardcore"}
        normalized = value.strip().capitalize()
        return normalized if normalized in allowed else "Chill"
