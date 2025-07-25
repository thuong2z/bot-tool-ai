import sqlite3

def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance INTEGER DEFAULT 0,
        ref_by INTEGER,
        last_checkin TEXT
    )""")
    conn.commit()
    conn.close()

def add_user(user_id, username, ref_by=None):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users(user_id, username, ref_by) VALUES(?,?,?)",
              (user_id, username, ref_by))
    conn.commit()
    conn.close()

def update_balance(user_id, amount):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else 0

def set_checkin(user_id, date):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE users SET last_checkin=? WHERE user_id=?", (date, user_id))
    conn.commit()
    conn.close()

def get_checkin(user_id):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT last_checkin FROM users WHERE user_id=?", (user_id,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else None

def total_users():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    res = c.fetchone()
    conn.close()
    return res[0] if res else 0