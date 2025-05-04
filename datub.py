import sqlite3
import os

# iegūst ceļu (kā app.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "gramatas.db")

#pievienojas datubāzei
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

#tabulas izveide
cur.execute("""
CREATE TABLE IF NOT EXISTS gramatas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums TEXT NOT NULL,
    gads TEXT NOT NULL,
    autors TEXT NOT NULL,
    zanrs TEXT NOT NULL,
    isuma TEXT NOT NULL,
    statuss TEXT
)
""")

conn.commit()
conn.close()

print("✅ Datubāze un tabula 'gramatas' izveidota.")
