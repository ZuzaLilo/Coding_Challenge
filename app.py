from flask import Flask, request
import sqlite3, json

app = Flask(__name__)

invalid_request_count = 0
total_request_count = 0


@app.route('/', methods = ['POST'])
def index():
    connection = sqlite3.connect('database.db')

    total_request_count  = total_request_count + 1

    # Sample JSON
    # {
    #     "customerID": 1,
    #     "tagID": 2,
    #     "userID": "aaaaaaaa-bbbb-cccc-1111-222222222222",
    #     "remoteIP": "123.234.56.78",
    #     "timestamp": 1500000000
    # }

    try:
        data = json.loads(request.data)
        customerID, tagID, userID, remoteIP, timestamp = (data['customerID'], data['tagID'], data['userID'], data['remoteIP'], data['timestamp'])
    except (ValueError, KeyError, TypeError):

        invalid_request_count = invalid_request_count + 1

        return 'Invalid request!'



    cur = connection.cursor()
    customers = cur.execute('SELECT * FROM customer').fetchall()

    connection.close()

    return str(customerID) + str(tagID) + str(userID) + str(remoteIP) + str(timestamp)



if __name__ == '__main__':
    app.run(debug = True, port=5000)