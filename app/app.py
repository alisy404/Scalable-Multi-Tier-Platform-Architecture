import psycopg2
from fastapi import FastAPI
from time import sleep
from config import APP_ENV, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

app = FastAPI(title="Tier-2 Database Service")


# -------------------------
# Database Connection
# -------------------------
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


# -------------------------
# Startup: Init DB
# -------------------------
@app.on_event("startup")
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            value TEXT NOT NULL
        )
    """
    )

    cur.execute(
        """
        INSERT INTO items (value)
        SELECT * FROM (VALUES ('alpha'), ('beta'), ('gamma')) AS v(value)
        WHERE NOT EXISTS (SELECT 1 FROM items)
    """
    )

    conn.commit()
    cur.close()
    conn.close()


# -------------------------
# Routes
# -------------------------
@app.get("/")
def root():
    return {"message": "Tier-2 service running", "endpoints": ["/health", "/data/{id}"]}


@app.get("/health")
def health():
    return {"status": "ok", "environment": APP_ENV}


@app.get("/data/{item_id}")
def get_data(item_id: int):
    sleep(0.1)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT value FROM items WHERE id = %s", (item_id,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return {"error": "item not found"}

    return {"id": item_id, "value": row[0], "source": "database"}
