import json
import os.path
import sqlite3


def connect(path):
    exists = os.path.exists(path)
    conn = sqlite3.connect(path)
    if not exists:
        create_tables(conn)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            contents TEXT,
            cost REAL
        )
    ''')
    conn.commit()


def get_cart(username: str) -> list:
    with connect('carts.db') as conn:
        cursor = conn.execute('SELECT * FROM carts WHERE username = ?', (username,))
        cart = cursor.fetchall()
        return [dict(row) for row in cart]


def add_to_cart(username: str, product_id: int):
    with connect('carts.db') as conn:
        cursor = conn.execute('SELECT contents FROM carts WHERE username = ?', (username,))
        row = cursor.fetchone()
        contents = json.loads(row['contents']) if row and row['contents'] else []
        contents.append(product_id)
        conn.execute('''
            INSERT INTO carts (username, contents, cost)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET contents = excluded.contents
        ''', (username, json.dumps(contents), 0))
        conn.commit()


def remove_from_cart(username: str, product_id: int):
    with connect('carts.db') as conn:
        cursor = conn.execute('SELECT contents FROM carts WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row and row['contents']:
            contents = json.loads(row['contents'])
            if product_id in contents:
                contents.remove(product_id)
                conn.execute('''
                    INSERT INTO carts (username, contents, cost)
                    VALUES (?, ?, ?)
                    ON CONFLICT(username) DO UPDATE SET contents = excluded.contents
                ''', (username, json.dumps(contents), 0))
                conn.commit()


def delete_cart(username: str):
    with connect('carts.db') as conn:
        conn.execute('DELETE FROM carts WHERE username = ?', (username,))
        conn.commit()
