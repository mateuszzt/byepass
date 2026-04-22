import sqlite3
from datetime import datetime

DB_NAME = "passwords.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        password_plain TEXT,
        sha256 TEXT,
        sha1 TEXT,
        bcrypt TEXT,
        salt BLOB,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        method TEXT,
        result TEXT,
        time REAL,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_password(password, sha256, sha1, bcrypt_hash, salt):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO passwords (password_plain, sha256, sha1, bcrypt, salt, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (password, sha256, sha1, bcrypt_hash, salt, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def save_attack(method, result, time_taken):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO attacks (method, result, time, created_at)
    VALUES (?, ?, ?, ?)
    """, (method, result, time_taken, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_passwords():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM passwords ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_attacks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attacks ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows

def get_password_by_id(password_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM passwords WHERE id = ?", (password_id,))
    row = cursor.fetchone()

    conn.close()
    return row