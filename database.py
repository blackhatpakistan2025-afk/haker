# database.py
import sqlite3
import os

def init_db():
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE users
                     (user_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, referral_code TEXT, referral_count INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE usage_logs
                     (log_id INTEGER PRIMARY KEY, user_id INTEGER, action TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

def add_user(user_id, first_name, last_name, referral_code=None):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, first_name, last_name, referral_code) VALUES (?, ?, ?, ?)",
              (user_id, first_name, last_name, referral_code))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def log_action(user_id, action):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO usage_logs (user_id, action) VALUES (?, ?)", (user_id, action))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT user_id) FROM usage_logs")
    active_users = c.fetchone()[0]
    c.execute("SELECT SUM(referral_count) FROM users")
    referral_count = c.fetchone()[0] or 0
    conn.close()
    return total_users, active_users, referral_count

def toggle_referrals(state):
    global REFERRAL_ENABLED
    REFERRAL_ENABLED = state