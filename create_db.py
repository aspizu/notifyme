import sqlite3
from pathlib import Path

Path("1.db").unlink(missing_ok=True)

con = sqlite3.connect("1.db")
cur = con.cursor()
cur.executescript(open("schema.sql").read())
con.commit()
con.close()
