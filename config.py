import sqlite3
from datetime import datetime

conn2 = sqlite3.connect('statistic.db')
cur2 = conn2.cursor()

conn = sqlite3.connect('db.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS settings(
   key TEXT PRIMARY KEY,
   value TEXT);
""")
conn.commit()
cur.execute("""CREATE TABLE IF NOT EXISTS fish(
    name TEXT PRIMARY KEY,
    R INT,
    G INT,
    B INT);
""")
conn.commit()

def setFishValue(key, r, g, b):
    cur.execute("INSERT OR IGNORE INTO fish VALUES (?, ?, ?, ?);", (key, r, g, b))
    cur.execute("UPDATE fish SET R = ?, G = ?, B = ? WHERE name=?", (r, g, b, key))
    conn.commit()


def getAllFish():
    cur.execute("SELECT * FROM fish;")
    result = cur.fetchall()
    return result


def deleteFish(key):
    cur.execute("DELETE FROM fish WHERE name = ?;", (key,))
    conn.commit()


def setSettingValue(key, value):
    cur.execute("INSERT OR IGNORE INTO settings VALUES (?, ?);", (key, value,))
    cur.execute("UPDATE settings SET value = ? WHERE key=?", (value, key))
    conn.commit()

def getAllSettingValues():
    cur.execute("SELECT * FROM settings;")
    result = cur.fetchall()
    return result

def getSettingsValue(key):
    cur.execute("INSERT OR IGNORE INTO settings VALUES (?, ?);", (key, ""))
    conn.commit()
    cur.execute("SELECT * FROM settings WHERE key = ?;", (key, ))
    one_result = cur.fetchone()
    return one_result[1]