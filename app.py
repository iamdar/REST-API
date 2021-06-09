from flask import Flask, jsonify, render_template, request
import os
import psycopg2

app = Flask(__name__)


def sql(query):
    if os.path.isfile(".env"):
        # load .env file
        from dotenv import load_dotenv
        load_dotenv()
        db_url = os.getenv("DATABASE_URL")
        db_name = os.getenv("DB_NAME")
        db_username = os.getenv("DB_USERNAME")
        db_password = os.getenv("DB_PASSWORD")
        conn = psycopg2.connect(database=db_name, user=db_username, password=db_password, host=db_url,
                                port="5432")
    else:
        # Heroku
        db_url = os.environ.get("DATABASE_URL", None)
        conn = psycopg2.connect(db_url, sslmode='require')
    cur = conn.cursor()
    if query[:6].lower() == "select":
        cur.execute(f"{query};")
        result = success(True, result=cur.fetchall())
    else:
        cur.execute(f"{query};")
        conn.commit()
        result = success(True)
    cur.close()
    conn.close()
    return result


def success(value, **kwargs):
    result = {"success": value}
    if value:
        status_code = 200
    else:
        status_code = 200

    if len(kwargs.items()) > 0:
        payload = {}
        for key, item in kwargs.items():
            payload[key] = item
        result["payload"] = payload

    return jsonify(result), status_code


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


@app.route("/item_<item_id>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def item_action(item_id):
    method = request.method.lower()
    # HTTP POST - Create Record
    if method == "post":
        result = "Creating new record"
    # HTTP PUT - Update Record
    elif method == "put":
        result = "Updating whole record"
    # HTTP PATCH - Update Record
    elif method == "patch":
        result = "Updating piece of record"
    # HTTP DELETE - Delete Record
    elif method == "delete":
        result = "Deleting the record"
    # HTTP GET - Read Record
    else:
        result = "Displaying record"
    return success(True, msg=result)


if __name__ == '__main__':
    app.run(debug=True)
