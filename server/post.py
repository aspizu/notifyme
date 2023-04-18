import json
from typing import Any

from starlette.requests import Request

from . import main, sql
from .misc import RESPONSE, Error
from .session import Session


@main.GET("/api/get_post")
async def get_post(request: Request, session: Session, id: int) -> RESPONSE:
    _, cur = main.db()
    row = cur.execute(
        """SELECT p.content, p.tags, p.recipients, p.created_time,
           u.id as author_id,
           u.username as author_username,
           u.display_name as author_display_name,
           u.avatar_url as author_avatar_url,
           u.tags as author_tags,
           u.permission as author_permission,
           u.created_time as author_created_time
           FROM post p, user u
           WHERE p.id = ? AND u.id = p.author_id""",
        [id],
    ).fetchone()
    if row is None:
        raise Error("Post not found.")
    tags: list[str] = json.loads(row["tags"])
    recipients: list[str] = json.loads(row["recipients"])
    if not (session.username in recipients or any(tag in tags for tag in session.tags)):
        raise Error("Not subscribed.")
    rows = cur.execute(
        """SELECT 
           emoji,
           COUNT(*) AS count,
           COUNT(
               CASE WHEN reaction.user_id = ? THEN TRUE ELSE FALSE END
           ) AS is_user_reaction
           FROM reaction
           WHERE post_id = ?
           GROUP BY emoji""",
        [session.user_id, id],
    ).fetchall()
    reactions: dict[int, tuple[int, bool]] = {
        row["emoji"]: (row["count"], bool(row["is_user_reaction"])) for row in rows
    }
    return {
        "id": id,
        "author": {
            "id": row["author_id"],
            "username": row["author_username"],
            "display_name": row["author_display_name"],
            "avatar_url": row["author_avatar_url"],
            "tags": json.loads(row["author_tags"]),
            "permission": row["author_permission"],
            "created_time": row["author_created_time"],
        },
        "content": row["content"],
        "tags": tags,
        "recipients": recipients,
        "created_time": row["created_time"],
        "reactions": reactions,
    }


@main.GET("/api/get_posts")
async def get_posts(request: Request, session: Session) -> RESPONSE:
    _, cur = main.db()
    rows = cur.execute(
        """SELECT p.id, p.content, p.tags, p.recipients, p.created_time,
           u.id as author_id,
           u.username as author_username,
           u.display_name as author_display_name,
           u.avatar_url as author_avatar_url,
           u.tags as author_tags,
           u.permission as author_permission,
           u.created_time as author_created_time
           FROM post p, user u
           WHERE u.id = p.author_id""",
        [],
    ).fetchall()
    posts: list[Any] = []  # Problems with typing I CANNOT solve!
    for row in rows:
        tags: list[str] = json.loads(row["tags"])
        recipients: list[str] = json.loads(row["recipients"])
        if not (
            session.username in recipients or any(tag in tags for tag in session.tags)
        ):
            continue
        rows2 = cur.execute(
            """SELECT 
               emoji,
               COUNT(*) AS count,
               COUNT(
                   CASE WHEN reaction.user_id = ? THEN 1 ELSE 0 END
               ) AS is_user_reaction
               FROM reaction
               WHERE post_id = ?
               GROUP BY emoji""",
            [session.user_id, id],
        ).fetchall()
        reactions: dict[int, tuple[int, bool]] = {
            row["emoji"]: (row["count"], bool(row["is_user_reaction"])) for row in rows2
        }
        posts.append(
            {
                "id": row["id"],
                "author": {
                    "id": row["author_id"],
                    "username": row["author_username"],
                    "display_name": row["author_display_name"],
                    "avatar_url": row["author_avatar_url"],
                    "tags": json.loads(row["author_tags"]),
                    "permission": row["author_permission"],
                    "created_time": row["created_time"],
                },
                "content": row["content"],
                "tags": tags,
                "recipients": recipients,
                "created_time": row["created_time"],
                "reactions": reactions,
            }
        )
    return {"posts": posts}


@main.POST("/api/new_post", permissions=(1,))
async def new_post(
    request: Request,
    session: Session,
    content: str,
    tags: list[str],
    recipients: list[str],
) -> RESPONSE:
    con, cur = main.db()
    cur.execute(
        """INSERT INTO post (author_id, content, tags, recipients)
           VALUES (?, ?, ?, ?)""",
        (session.user_id, content, json.dumps(tags), json.dumps(recipients)),
    )
    con.commit()
    return {"id": cur.lastrowid}


@main.POST("/api/edit_post", permissions=(1,))
async def edit_post(
    request: Request,
    session: Session,
    id: int,
    content: str | None,
    tags: list[str] | None,
    recipients: list[str] | None,
) -> RESPONSE:
    con, cur = main.db()
    row = cur.execute("SELECT author_id FROM post WHERE id = ?", [id]).fetchone()
    if row is None:
        raise Error("Post not found.")
    if row["author_id"] != session.user_id:
        raise Error("Not author.")
    cur.execute(
        *sql.update(
            "post",
            set={"content": content, "tags": tags, "recipients": recipients},
            where="id = ?",
            args=[id],
        )
    )
    con.commit()
    return {}


@main.POST("/api/delete_post", permissions=(1,))
async def delete_post(request: Request, session: Session, id: int) -> RESPONSE:
    con, cur = main.db()
    row = cur.execute("SELECT author_id FROM post WHERE id = ?", [id]).fetchone()
    if row is None:
        raise Error("Post not found.")
    if row["author_id"] != session.user_id:
        raise Error("Not author.")
    cur.execute("DELETE FROM post WHERE id = ?", [id])
    con.commit()
    return {}
