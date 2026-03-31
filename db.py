import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": "attendance_system",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'student'))
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION
        );
    """)

    # Admin-configurable campus location
    cur.execute("""
        CREATE TABLE IF NOT EXISTS campus_location (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL DEFAULT 'College Campus',
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            radius INTEGER NOT NULL DEFAULT 100,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Student academic profile details
    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            full_name TEXT,
            degree TEXT,
            branch TEXT,
            specialization TEXT,
            year TEXT,
            section TEXT,
            is_complete BOOLEAN DEFAULT FALSE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Subjects managed by admin
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            total_hours INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Many-to-many: which students are assigned which subjects
    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_subjects (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
            UNIQUE(user_id, subject_id)
        );
    """)

    # Add subject_id column to attendance if it doesn't exist
    cur.execute("""
        ALTER TABLE attendance
        ADD COLUMN IF NOT EXISTS subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL;
    """)

    # Seed a default campus location if none exists
    cur.execute("SELECT COUNT(*) FROM campus_location")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO campus_location (name, latitude, longitude, radius)
            VALUES ('College Campus', 12.9716, 77.5946, 100)
        """)

    conn.commit()
    cur.close()
    conn.close()


def get_campus_location():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM campus_location ORDER BY id DESC LIMIT 1")
    loc = cur.fetchone()
    cur.close()
    conn.close()
    return loc


def get_student_profile(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM student_profiles WHERE user_id = %s", (user_id,))
    profile = cur.fetchone()
    cur.close()
    conn.close()
    return profile
