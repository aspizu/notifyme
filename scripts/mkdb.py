import os
import sqlite3

database = "database.db"
os.remove(database)
con = sqlite3.connect(database)
cur = con.cursor()
cur.executescript(open("server/schema.sql").read())
con.commit()
