import sqlite3

from starlette.requests import Request

from . import main
from .misc import RESPONSE, Error
from .session import Session


@main.POST("/api/add_reaction")
async def add_reaction(
    request: Request, session: Session, post_id: int, emoji: int
) -> RESPONSE:
    con, cur = main.db()
    try:
        cur.execute(
            "INSERT INTO reaction (emoji, post_id, user_id) VALUES (?, ?, ?)",
            [emoji, post_id, session.user_id],
        )
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in e.args[0]:
            raise Error("Reaction exists.")
    con.commit()
    return {}


@main.POST("/api/remove_reaction")
async def remove_reaction(
    request: Request, session: Session, post_id: int, emoji: int
) -> RESPONSE:
    con, cur = main.db()
    cur.execute(
        "DELETE FROM reaction WHERE emoji = ? AND post_id = ? and user_id = ?",
        [emoji, post_id, session.user_id],
    )
    con.commit()
    return {}
