import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()
con.executescript(open("server/schema.sql").read())
con.commit()
