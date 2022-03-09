from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    connection = sqlite3.connect('database.db')

    cur = connection.cursor()
    customers = cur.execute('SELECT * FROM customer').fetchall()

    connection.close()

    return str(customers)



if __name__ == '__main__':
    app.run(debug = True, port=5000)