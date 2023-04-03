import json
from dataclasses import dataclass

from ..lib import db


@dataclass
class User:
    id: int
    username: str
    displayname: str
    tags: list[str]
    time: int

    def json(self):
        return dict(
            id=self.id,
            username=self.username,
            displayname=self.displayname,
            tags=self.tags,
            time=self.time,
        )


def get_user(username: str) -> User:
    con = db()
    cur = con.cursor()
    cur.execute(
        "SELECT id, username, displayname, tags, time FROM user WHERE username = ?",
        [username],
    )
    row = cur.fetchone()
    if row is None:
        raise ValueError
    con.commit()
    con.close()
    return User(row[0], row[1], row[2], json.loads(row[3]), row[4])
