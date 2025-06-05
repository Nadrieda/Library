import psycopg2

# TODO: Maybe use .env? Better pratice
def get_connection():
    return psycopg2.connect(
        database="DIS-Project",
        user="postgres",
        password="nCUV0YDEL49Ejr",
        host="localhost",
        port="5432"
    )