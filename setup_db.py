from db import get_connection

# Initialize database ! :D
with open("init_db.sql", "r") as f:
    sql = f.read()

conn = get_connection()

cur = conn.cursor()
cur.execute(sql)
conn.commit()
cur.close()
conn.close()

print("Database initialized.")