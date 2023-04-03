import json
import sqlite3
from pathlib import Path

Path("1.db").unlink(missing_ok=True)

con = sqlite3.connect("1.db")
cur = con.cursor()
cur.executescript(open("schema.sql").read())

fictional = json.loads(open("fictional.json", "r").read())


for user in fictional["users"]:
    cur.execute(
        "INSERT INTO user (username, password_hash, displayname, tags, time) "
        "VALUES (?, ?, ?, ?, ?)",
        [
            user["username"],
            "FICTIONAL",
            user["displayname"],
            json.dumps(user["tags"]),
            0,
        ],
    )
for notification in fictional["notifications"]:
    cur.execute(
        "INSERT INTO notification (author, content, tags, recipients, time) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            notification["author"],
            notification["content"],
            json.dumps(notification["tags"]),
            json.dumps(notification["recipients"]),
            notification["time"],
        ),
    )


con.commit()
con.close()
