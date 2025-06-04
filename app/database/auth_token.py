import secrets
from typing import TYPE_CHECKING
from datetime import datetime, timedelta, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import ModelPrettyPrint

if TYPE_CHECKING:
    from .user import User


class AuthToken(ModelPrettyPrint):
    __tablename__ = "auth_tokens"

    token: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="tokens")

    @staticmethod
    async def generate_auth_token(session: AsyncSession, user_id: int) -> "AuthToken":
        token = secrets.token_urlsafe(32)
        auth_token = AuthToken(
            token=token,
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        session.add(auth_token)
        await session.commit()
        return auth_token
