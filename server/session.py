import hashlib
import json
import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING

from starlette.requests import Request

from .misc import Error

if TYPE_CHECKING:
    from .main import Main


def is_username_valid(username: str) -> bool:
    return (4 <= len(username) <= 32) and username.isalnum()


def is_password_valid(password: str) -> bool:
    return 8 <= len(password)


def hash_password(password: str, username: str) -> str:
    return hashlib.sha256((password + username).encode()).hexdigest()


@dataclass
class Session:
    token: str
    user_id: int
    username: str
    permission: int
    tags: list[str]


class Sessions:
    def __init__(self, main: "Main") -> None:
        self.sessions: dict[str, Session] = {}
        self.main = main

    def get_session(self, request: Request) -> Session | None:
        return self.sessions.get(request.cookies.get("token", ""))

    def new_session(self, username: str, password: str) -> Session:
        row = self.main.db_fetchone(
            "SELECT password_hash, permission, id, tags FROM user WHERE username = ?",
            [username],
        )
        if row is None:
            raise Error("Username not found.")
        password_hash: str = row["password_hash"]
        permission: int = row["permission"]
        user_id: int = row["id"]
        tags: list[str] = json.loads(row["tags"])
        if hash_password(password, username) != password_hash:
            raise Error("Password is incorrect.")
        token = secrets.token_urlsafe()
        self.sessions[token] = Session(token, user_id, username, permission, tags)
        return self.sessions[token]

    def remove_session(self, session_or_token: Session | str) -> None:
        self.sessions.pop(
            session_or_token.token
            if isinstance(session_or_token, Session)
            else session_or_token,
            None,
        )

    def remove_all_sessions(self, username: str) -> None:
        for session in [
            session
            for session in self.sessions.values()
            if session.username == username
        ]:
            self.remove_session(session)
