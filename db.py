import sqlite3

from pathlib import Path


# =====================================================
# DATABASE LOCATION
# =====================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent.parent


DATABASE_DIR = (
    BASE_DIR /
    "database"
)


DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


DATABASE_FILE = (
    DATABASE_DIR /
    "skinsense.db"
)


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


# =====================================================
# CREATE DATABASE TABLE
# =====================================================

def init_database():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        CREATE TABLE IF NOT EXISTS scans (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            created_at TEXT NOT NULL,

            filename TEXT NOT NULL,

            quality REAL NOT NULL,

            condition TEXT NOT NULL,

            confidence REAL NOT NULL,

            risk TEXT NOT NULL

        )

    """)


    connection.commit()

    connection.close()


# =====================================================
# SAVE SCAN
# =====================================================

def save_scan(

    created_at,

    filename,

    quality,

    condition,

    confidence,

    risk

):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        INSERT INTO scans (

            created_at,

            filename,

            quality,

            condition,

            confidence,

            risk

        )

        VALUES (?, ?, ?, ?, ?, ?)

    """, (

        created_at,

        filename,

        quality,

        condition,

        confidence,

        risk

    ))


    connection.commit()

    connection.close()


# =====================================================
# GET HISTORY
# =====================================================

def get_history():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        SELECT

            id,

            created_at,

            filename,

            quality,

            condition,

            confidence,

            risk

        FROM scans

        ORDER BY id DESC

        LIMIT 20

    """)


    rows = cursor.fetchall()


    connection.close()


    return [

        dict(row)

        for row in rows

    ]