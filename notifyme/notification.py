import json
from typing import Any

from starlette.requests import Request
from starlette.responses import Response

from . import app
from .lib import db, failed_response, successful_response
from .session import Session


@app.GET("/api/notification/{id}", require_logged_in=False)
async def get_notification(request: Request, id: str) -> Response:
    con = db()
    cur = con.cursor()
    cur.execute(
        "SELECT author, content, tags, recipients, time "
        "FROM notification WHERE id = ?",
        [id],
    )
    row = cur.fetchone()
    if row is None:
        return failed_response("notification not found")
    author: str = row[0]
    content: str = row[1]
    tags: list[str] = json.loads(row[2])
    recipients: list[str] = json.loads(row[3])
    time: int = row[4]
    cur.execute(
        "SELECT username, displayname, tags, time FROM user WHERE id = ?", [author]
    )
    row = cur.fetchone()
    if row is None:
        return failed_response("fucked up database")
    con.commit()
    con.close()
    return successful_response(
        author=dict(
            username=row[0],
            displayname=row[1],
            tags=json.loads(row[2]),
            time=row[3],
        ),
        content=content,
        tags=tags,
        recipients=recipients,
        time=time,
    )


@app.GET("/api/feed")
async def get_feed(
    request: Request, session: Session, limit: int | None, offset: int | None
) -> Response:
    user = session.get_user()
    limit = limit or 20
    offset = offset or 0
    con = db()
    cur = con.cursor()
    cur.execute(
        "SELECT n.id, n.content, n.tags, n.recipients, n.time, "
        "       u.username, u.displayname, u.tags, u.time "
        "FROM notification n, user u "
        "WHERE n.author = u.id "
        "ORDER BY n.time DESC LIMIT ? OFFSET ?",
        [limit, offset],
    )
    rows = cur.fetchall()
    con.commit()
    con.close()
    feed: list[Any] = []
    for row in rows:
        id: int = row[0]
        content: str = row[1]
        tags: list[str] = json.loads(row[2])
        recipients: list[str] = json.loads(row[3])
        time: int = row[4]
        author_username: str = row[5]
        author_displayname: str = row[6]
        author_tags: list[str] = json.loads(row[7])
        author_time: int = row[5]
        if (
            any(users_tag in tags for users_tag in user.tags)
            or user.username in recipients
        ):
            feed.append(
                dict(
                    id=id,
                    author=dict(
                        username=author_username,
                        displayname=author_displayname,
                        tags=author_tags,
                        time=author_time,
                    ),
                    content=content,
                    tags=[tag for tag in tags if tag in user.tags],
                    for_you=user.username in recipients,
                    time=time,
                )
            )
    return successful_response(feed=feed)
