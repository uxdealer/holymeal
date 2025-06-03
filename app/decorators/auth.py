from functools import wraps
from flask import request, g, abort
from datetime import datetime, timezone

from app.database.db_session import sync_sessionmaker
from app.database.auth_token import AuthToken
from app.database.user import User


def require_auth_token():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            with sync_sessionmaker() as session:
                token = request.cookies.get("Authorization")
                if not token:
                    return abort(401, "❌ Токен обязателен")

                auth_token: AuthToken = (
                    session.query(AuthToken).filter_by(token=token).first()
                )

                if not auth_token:
                    return abort(401, "❌ Неверный токен")

                if auth_token.used:
                    return abort(401, "⚠️ Токен уже использован")

                if datetime.now(timezone.utc) >= auth_token.expires_at.replace(
                    tzinfo=timezone.utc
                ):
                    return abort(401, "⏳ Токен просрочен")

                g.user = session.query(User).get(auth_token.user_id)
                g.auth_token = auth_token

                return f(*args, **kwargs)

        return wrapped

    return decorator
