import sqlite3
from getpass import getpass
from passlib.context import CryptContext

DB_PATH = "users.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        conn.commit()

def create_user(username: str, password: str):
    hashed_password = pwd_context.hash(password)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            print(f"✅ User '{username}' created successfully.")
        except sqlite3.IntegrityError:
            print(f"⚠️ User '{username}' already exists.")

if __name__ == "__main__":
    init_db()
    username = input("Enter username: ").strip()
    password = getpass("Enter password: ").strip()
    confirm = getpass("Confirm password: ").strip()

    if password != confirm:
        print("❌ Passwords do not match.")
    elif not username or not password:
        print("❌ Username and password must not be empty.")
    else:
        create_user(username, password)
