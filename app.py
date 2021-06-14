from flask import Flask, jsonify, render_template, request
import os
import psycopg2
import urllib.parse

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
        # db_schema = os.getenv("DB_SCHEMA")
        conn = psycopg2.connect(database=db_name, user=db_username, password=db_password, host=db_url,
                                port="5432")
    else:
        # Heroku
        db_url = os.environ.get("DATABASE_URL", None)
        # db_schema = os.getenv("DB_SCHEMA")
        conn = psycopg2.connect(db_url, sslmode='require')
    cur = conn.cursor()

    # check if tables exist
    cur.execute("select * from information_schema.tables where table_name='items'")
    if not (bool(cur.rowcount)):
        cur.execute(f"CREATE TABLE items (id serial PRIMARY KEY, laz_link text, ia_link text, cat varchar);")
        conn.commit()
    cur.execute("select * from information_schema.tables where table_name='quotes'")
    if not (bool(cur.rowcount)):
        cur.execute(f"CREATE TABLE quotes (id serial PRIMARY KEY, content text, author text, cat varchar);")
        conn.commit()

    if query[:6].lower() == "select":
        cur.execute(f"{query};")
        result = success(True, result=cur.fetchall())
    elif query[:6].lower() == "post":
        cur.execute(f"{query};")
        conn.commit()
        id_of_new_row = cur.fetchone()[0]
        result = success(True, item_id=id_of_new_row)
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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/items", methods=["GET", "POST", "PATCH", "DELETE"])
def items_action():
    method = request.method.lower()
    item_id = request.args.get("item_id")
    laz_link = request.args.get("laz_link")
    ia_link = request.args.get("ia_link")
    cat = ""
    try:
        cat = urllib.parse.quote(request.args.get("cat"))
    except TypeError as e:
        print(e)
    # HTTP POST - Create Record
    if method == "post":
        result = sql(f"INSERT INTO items (laz_link, ia_link, cat) VALUES ('{laz_link}', '{ia_link}', '{cat}' ) "
                     f"RETURNING id")
    # HTTP PUT - Update Record
    elif method == "put":
        result = "Updating whole record"
    # HTTP PATCH - Update Record
    elif method == "patch":
        if item_id is None:
            return success(False, msg="Missing required parameter(s) 'item_id'")
        record = sql(f"SELECT * FROM items WHERE id='{item_id}'")
        cur_laz_link = record[0].json["payload"]["result"][0][1]
        cur_ia_link = record[0].json["payload"]["result"][0][2]
        cur_cat = record[0].json["payload"]["result"][0][3]
        fields = ["laz_link", "ia_link", "cat"]
        cur_item = [cur_laz_link, cur_ia_link, cur_cat]
        sent_item = [laz_link, ia_link, cat]
        for i in range(0, len(cur_item)):
            if not (cur_item[i].lower() == sent_item[i].lower()):
                sql(f"UPDATE items SET {fields[i]}='{sent_item[i]}' "
                    f"WHERE id='{item_id}'")

        result = success(True, item_id=item_id)
    # HTTP DELETE - Delete Record
    elif method == "delete":
        if item_id is None:
            return success(False, msg="Missing required parameter(s) 'item_id'")
        result = sql(f"DELETE FROM items WHERE id='{item_id}' "
                     f"RETURNING id")
    # HTTP GET - Read Record
    else:
        if item_id:
            result = sql(f"SELECT * FROM items WHERE id='{item_id}'")
        else:
            result = sql("SELECT * FROM items")
    return result


@app.route("/quotes", methods=["GET", "POST", "PATCH", "DELETE"])
def quotes_action():
    method = request.method.lower()
    quote_id = request.args.get("quote_id")
    content = ""
    author = ""
    cat = ""

    try:
        content = urllib.parse.quote(request.args.get("content"))
    except TypeError as e:
        print(e)
    try:
        author = urllib.parse.quote(request.args.get("author"))
    except TypeError as e:
        print(e)
    try:
        cat = urllib.parse.quote(request.args.get("cat"))
    except TypeError as e:
        print(e)

    # HTTP POST - Create Record
    if method == "post":
        if content == "":
            return success(False, msg="Missing required parameter(s) 'content'")
        result = sql(f"INSERT INTO quotes (content, author, cat) VALUES ('{content}', '{author}', '{cat}' ) "
                     f"RETURNING id")
    # HTTP PUT - Update Record
    elif method == "put":
        result = "Updating whole record"
    # HTTP PATCH - Update Record
    elif method == "patch":
        if quote_id is None:
            return success(False, msg="Missing required parameter(s) 'quote_id'")
        record = sql(f"SELECT * FROM quotes WHERE id='{quote_id}'")
        cur_content = record[0].json["payload"]["result"][0][1]
        cur_author = record[0].json["payload"]["result"][0][2]
        cur_cat = record[0].json["payload"]["result"][0][3]
        fields = ["content", "author", "cat"]
        cur_item = [cur_content, cur_author, cur_cat]
        sent_item = [content, author, cat]
        for i in range(0, len(cur_item)):
            # print(f"{cur_item[i].lower()} {sent_item[i].lower()}")
            if not (cur_item[i].lower() == sent_item[i].lower()):
                sql(f"UPDATE quotes SET {fields[i]}='{sent_item[i]}' "
                    f"WHERE id='{quote_id}'")

        result = success(True, item_id=quote_id)
    # HTTP DELETE - Delete Record
    elif method == "delete":
        if quote_id is None:
            return success(False, msg="Missing required parameter(s) 'quote_id'")
        result = sql(f"DELETE FROM quotes WHERE id='{quote_id}' "
                     f"RETURNING id")
    # HTTP GET - Read Record
    else:
        if quote_id:
            result = sql(f"SELECT * FROM quotes WHERE id='{quote_id}'")
        else:
            result = sql("SELECT * FROM quotes")
    return result


if __name__ == '__main__':
    app.run()
