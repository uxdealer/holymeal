"""
Маршруты для работы с авторизацией
"""

from datetime import datetime, timezone
from flask import Blueprint, Response, make_response, redirect
from sqlalchemy import select
from app.database.auth_token import AuthToken
from app.utils.logger import setup_logger
from app.database.db_session import sync_sessionmaker

logger = setup_logger(__name__)
auth_routes = Blueprint("auth_router", __name__)


@auth_routes.route("/auth/<token>", methods=["GET"])
def auth(token: str):
    with sync_sessionmaker() as session:
        stmt = select(AuthToken).where(AuthToken.token == token)
        auth_token = session.execute(stmt).scalar_one_or_none()

        if auth_token is None:
            return Response(status=401)
        else:
            if datetime.now(timezone.utc) >= auth_token.expires_at.replace(
                tzinfo=timezone.utc
            ):
                return Response(status=401)
            else:
                response = make_response(redirect("/"))
                response.set_cookie(
                    key="Authorization",
                    value=auth_token.token,
                    httponly=True,
                    secure=True,
                    samesite="Lax",
                    max_age=3600,
                )
                return response
