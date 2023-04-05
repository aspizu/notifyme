import json

from starlette.requests import Request

from . import main, sql
from .misc import RESPONSE, Error
from .session import Session, hash_password, is_password_valid, is_username_valid


@main.POST("/api/login", require_logged_in=False)
async def login(request: Request, username: str, password: str) -> RESPONSE:
    return {"token": main.sessions.new_session(username, password).token}


@main.POST("/api/logout")
async def logout(request: Request, session: Session) -> RESPONSE:
    main.sessions.remove_session(session)
    return {}


@main.POST("/api/register", require_logged_in=False)
async def register(
    request: Request, username: str, display_name: str, password: str
) -> RESPONSE:
    if not is_username_valid(username):
        raise Error("Username is invalid.")
    if not is_password_valid(password):
        raise Error("Password is invalid.")
    con, cur = main.db()
    row = cur.execute("SELECT id FROM user WHERE username = ?", [username]).fetchone()
    if row is not None:
        raise Error("Username already exists.")
    cur.execute(
        "INSERT INTO user (username, display_name, password_hash) VALUES (?, ?, ?)",
        [username, display_name, hash_password(password, username)],
    )
    con.commit()
    return {"id": cur.lastrowid}


@main.POST("/api/change_password", require_logged_in=False)
async def change_password(
    request: Request, username: str, old_password: str, new_password: str
) -> RESPONSE:
    if not is_password_valid(new_password):
        raise Error("New password is invalid.")
    con, cur = main.db()
    row = cur.execute(
        "SELECT password_hash FROM user WHERE username = ?", [username]
    ).fetchone()
    if row is None:
        raise Error("Username not found.")
    password_hash: str = row["password_hash"]
    if hash_password(old_password, username) != password_hash:
        raise Error("Old password is incorrect.")
    cur.execute(
        "UPDATE user SET password_hash = ? WHERE username = ?",
        [hash_password(new_password, username), username],
    )
    con.commit()
    main.sessions.remove_all_sessions(username)
    return {}


@main.POST("/api/edit_profile")
async def edit_profile(
    request: Request,
    session: Session,
    display_name: str | None,
    avatar_url: str | None,
    tags: list[str] | None,
) -> RESPONSE:
    if tags is not None:
        session.tags = tags
    con, cur = main.db()
    cur.execute(
        *sql.update(
            "user",
            set={
                "display_name": display_name,
                "avatar_url": avatar_url,
                "tags": json.dumps(tags) if tags is not None else None,
            },
            where="id = ?",
            args=[session.user_id],
        )
    )
    con.commit()
    return {}


@main.GET("/api/check_session")
async def check_session(request: Request, session: Session) -> RESPONSE:
    return {}


@main.GET("/api/get_user")
async def get_user(request: Request, session: Session, username: str) -> RESPONSE:
    row = main.db_fetchone(
        """SELECT id, display_name, avatar_url, tags, permission, created_time FROM user
           WHERE username = ?""",
        [username],
    )
    if row is None:
        raise Error("Username not found.")
    return {
        "id": row["id"],
        "username": username,
        "display_name": row["display_name"],
        "avatar_url": row["avatar_url"],
        "tags": json.loads(row["tags"]),
        "permission": row["permission"],
        "created_time": row["created_time"],
    }


@main.POST("/api/delete_user", require_logged_in=False)
async def delete_user(
    request: Request,
    username: str,
    password: str,
) -> RESPONSE:
    con, cur = main.db()
    row = cur.execute(
        "SELECT id, password_hash FROM user WHERE username = ?", [username]
    ).fetchone()
    if row is None:
        raise Error("Username not found.")
    id: str = row["id"]
    password_hash: str = row["password_hash"]
    if hash_password(password, username) != password_hash:
        raise Error("Password is incorrect.")
    cur.execute("DELETE FROM user WHERE id = ?", [id])
    cur.execute("DELETE FROM post WHERE author_id = ?", [id])
    cur.execute("DELETE FROM reaction WHERE user_id = ?", [id])
    con.commit()
    main.sessions.remove_all_sessions(username)
    return {}
