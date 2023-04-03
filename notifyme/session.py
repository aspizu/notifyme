import hashlib
import secrets
from dataclasses import dataclass

from starlette.requests import Request

from .db.user import get_user


@dataclass(frozen=True)
class Session:
    token: str
    username: str

    def get_user(self):
        return get_user(self.username)


def is_username_valid(username: str) -> bool:
    return (4 <= len(username) <= 32) and username.isalnum()


def is_password_valid(password: str) -> bool:
    return 8 <= len(password)


def hash_password(password: str, username: str) -> str:
    return hashlib.sha256((password + username).encode()).hexdigest()


class Sessions:
    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}  # tokens to Sessions

    def get(self, request: Request) -> Session | None:
        return self.sessions.get(request.cookies.get("token", ""), None)

    def new(self, username: str) -> Session:
        token = secrets.token_urlsafe()
        self.sessions[token] = Session(token, username)
        return self.sessions[token]

    def remove(self, session_or_token: Session | str) -> None:
        self.sessions.pop(
            session_or_token.token
            if isinstance(session_or_token, Session)
            else session_or_token,
            None,
        )
