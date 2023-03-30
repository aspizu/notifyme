import json

from starlette.requests import Request
from starlette.responses import Response

from . import app
from .lib import db, failed_response, successful_response, time
from .session import Session, hash_password, is_password_valid, is_username_valid


@app.POST("/api/login", require_logged_in=False)
async def login(request: Request, username: str, password: str) -> Response:
    con = db()
    cur = con.cursor()
    cur.execute("SELECT password_hash FROM user WHERE username = ?", [username])
    row = cur.fetchone()
    if row is None:
        return failed_response("username not found")
    password_hash: str = row[0]
    if hash_password(password, username) != password_hash:
        return failed_response("password incorrect")
    con.close()
    return successful_response(token=app.sessions.new(username).token)


@app.POST("/api/logout")
async def logout(request: Request, session: Session) -> Response:
    app.sessions.remove(session.token)
    return successful_response()


@app.POST("/api/register", require_logged_in=False)
async def register(
    request: Request, username: str, password: str, displayname: str
) -> Response:
    if not is_username_valid(username):
        return failed_response("username invalid")
    if not is_password_valid(password):
        return failed_response("password invalid")
    con = db()
    cur = con.cursor()
    cur.execute("SELECT username FROM user WHERE username = ?", [username])
    row = cur.fetchone()
    if row is not None:
        return failed_response("username taken")
    cur.execute(
        "INSERT INTO user (username, password_hash, displayname, time) "
        "VALUES (?, ?, ?, ?)",
        [username, hash_password(password, username), displayname, time()],
    )
    con.commit()
    con.close()
    return successful_response(id=cur.lastrowid)


@app.POST("/api/change_password")
async def change_password(
    request: Request, session: Session, old_password: str, new_password: str
) -> Response:
    if not is_password_valid(new_password):
        return failed_response("new password invalid")
    con = db()
    cur = con.cursor()
    cur.execute("SELECT password_hash FROM user WHERE username = ?", [session.username])
    row = cur.fetchone()
    if row is None:
        return failed_response("username not found")
    password_hash: str = row[0]
    if hash_password(old_password, session.username) != password_hash:
        return failed_response("password incorrect")
    cur.execute(
        "UPDATE user SET password_hash = ? WHERE username = ?",
        [hash_password(new_password, session.username), session.username],
    )
    con.close()
    return successful_response()


@app.POST("/api/update_profile")
async def update_profile(
    request: Request, session: Session, displayname: str | None, tags: list[str] | None
) -> Response:
    fields: list[str] = []
    values: list[str] = []
    if displayname is not None:
        fields.append("displayname")
        values.append(displayname)
    if tags is not None:
        fields.append("tags")
        values.append(json.dumps(tags))
    if len(fields) == 0:
        return successful_response()
    query = (
        "UPDATE user SET "
        + "".join(f"{field} = ? " for field in fields)
        + "WHERE username = ?"
    )
    print(query)
    con = db()
    cur = con.cursor()
    cur.execute(query, [*values, session.username])
    return successful_response()


@app.GET("/api/check_session")
async def SQL(request: Request) -> Response:
    return successful_response()


@app.GET("/api/user/{username}", require_logged_in=False)
async def get_user(request: Request, username: str):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT displayname, tags FROM user WHERE username = ?", [username])
    row = cur.fetchone()
    if row is None:
        return failed_response("username not found")
    return successful_response(displayname=row[0], tags=json.loads(row[1]))
