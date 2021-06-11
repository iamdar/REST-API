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
        db_schema = os.getenv("DB_SCHEMA")
        conn = psycopg2.connect(database=db_name, user=db_username, password=db_password, host=db_url,
                                port="5432")
    else:
        # Heroku
        db_url = os.environ.get("DATABASE_URL", None)
        db_schema = os.getenv("DB_SCHEMA")
        conn = psycopg2.connect(db_url, sslmode='require')
    cur = conn.cursor()

    # check if table exist
    cur.execute("select * from information_schema.tables where table_name='items'")
    if not (bool(cur.rowcount)):
        cur.execute(f"{db_schema};")
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


@app.route("/item", methods=["GET", "POST", "PATCH", "DELETE"])
def item_action():
    method = request.method.lower()
    item_id = request.args.get("item_id")
    laz_link = request.args.get("laz_link")
    ia_link = request.args.get("ia_link")
    cat = request.args.get("cat")
    # HTTP POST - Create Record
    if method == "post":
        result = sql(f"INSERT INTO items (laz_link, ia_link, cat) VALUES ('{laz_link}', '{ia_link}', '{cat}' ) "
                     f"RETURNING id")
    # HTTP PUT - Update Record
    elif method == "put":
        result = "Updating whole record"
    # HTTP PATCH - Update Record
    elif method == "patch":
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
        result = sql(f"DELETE FROM items WHERE id='{item_id}' "
                     f"RETURNING id")
    # HTTP GET - Read Record
    else:
        if item_id:
            result = sql(f"SELECT * FROM items WHERE id='{item_id}'")
        else:
            result = sql("SELECT * FROM items")
    return result


if __name__ == '__main__':
    app.run()
