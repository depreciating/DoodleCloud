import psycopg2
import json
import time
from psycopg2.extras import RealDictCursor
from config_loader import CONF

def get_connection():
    try:
        return psycopg2.connect(
            host=CONF.get("DB_HOST"),
            database=CONF.get("DB_NAME"),
            user=CONF.get("DB_USER"),
            password=CONF.get("DB_PASS"),
            port=CONF.get("DB_PORT"),
            sslmode='require'
        )
    except: return None

def init_db():
    conn = get_connection()
    if not conn: return
    try:
        cur = conn.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS insta_files_v2 (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            media_ids TEXT NOT NULL, 
            is_converted BOOLEAN DEFAULT FALSE,
            created_at BIGINT
        );
        """
        cur.execute(query)
        conn.commit()
    except: pass
    finally: conn.close()

def save_file_record(filename, media_ids_list, is_converted):
    conn = get_connection()
    if not conn: return
    try:
        cur = conn.cursor()
        ids_json = json.dumps(media_ids_list)
        query = "INSERT INTO insta_files_v2 (filename, media_ids, is_converted, created_at) VALUES (%s, %s, %s, %s)"
        cur.execute(query, (filename, ids_json, is_converted, int(time.time())))
        conn.commit()
    except Exception as e: print(f"DB Save Error: {e}")
    finally: conn.close()

def list_files():
    conn = get_connection()
    if not conn: return []
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM insta_files_v2 ORDER BY created_at DESC")
        return cur.fetchall()
    except: return []
    finally: conn.close()

def delete_file_record(record_id):
    conn = get_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM insta_files_v2 WHERE id = %s", (record_id,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

init_db()