from flask import Flask, jsonify, render_template, request
import os
import psycopg2

app = Flask(__name__)


def sql(query):
    if os.path.isfile(".env"):
        # load .env file
        from dotenv import load_dotenv
        load_dotenv()
        DATABASE_URL = os.getenv("DATABASE_URL")
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        conn = psycopg2.connect(database="autobotdb", user=DB_USERNAME, password="P@s$w0rd", host=DATABASE_URL,
                                port="5432")
    else:
        # Heroku
        DATABASE_URL = os.environ.get("DATABASE_URL", None)
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    if query[:6].lower() == "select":
        cur.execute(f"{query};")
        result = cur.fetchall()
    else:
        cur.execute(f"{query};")
        conn.commit()
        result = "Database has been modified."
    cur.close()
    conn.close()
    return result


def create_table():
    query = "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar)"
    return sql(query)


def insert_record():
    query = "INSERT INTO test2 (num, data) VALUES ('12', 'Test')"
    return sql(query)


def insert_record():
    query = "INSERT INTO test2 (num, data) VALUES ('12', 'Test')"
    return sql(query)

def select_record():
    query = "SELECT * FROM test2"
    return sql(query)

@app.route("/")
def home():
    return render_template("index.html")

# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


# if __name__ == '__main__':
#     app.run(debug=True)
