import psycopg2

# Connect to default 'postgres' database to create our database
try:
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='123456',
        host='localhost',
        port='5432'
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'attendance_system'")
    exists = cur.fetchone()
    if not exists:
        cur.execute("CREATE DATABASE attendance_system")
        print("✅ Database 'attendance_system' created successfully!")
    else:
        print("ℹ️  Database 'attendance_system' already exists.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
