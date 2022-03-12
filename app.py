from flask import Flask, request
import sqlite3, json
from multiprocessing import Manager

app = Flask(__name__)

def create_hourly_stats():
    print(total_request_count)
    print(invalid_request_count)


# Empty stub function for valid requests
def process_request(customerID, tagID, userID, remoteIP, timestamp):
    print('Valid request')
    # pass


def checkValidJson(data):
    try:
        json_data = json.loads(data)
        customerID, tagID, userID, remoteIP, timestamp = (json_data['customerID'], json_data['tagID'], json_data['userID'], json_data['remoteIP'], json_data['timestamp'])

        if not isinstance(customerID, int):
            print('customerID must be a number!')
            return False
        
        if not isinstance(tagID, int):
            print('tagID must be a number!')
            return False
        
        if not isinstance(userID, str):
            print('userID must be a string!')
            return False
        
        if not isinstance(remoteIP, str):
            print('remoteIP must be a string!')
            return False

        if not isinstance(timestamp, int):
            print('timestamp must be a number!')
            return False

        return customerID, tagID, userID, remoteIP, timestamp

    except (ValueError, KeyError, TypeError):
        
        print('Invalid JSON!')
        return False



@app.route('/', methods = ['POST'])
def index():

    try:
        request_data = request.get_json()
        customer_id = request_data['customerID']
        total_request_count[customer_id] += 1
    except:
        print("Can't count request: can't find customer id!")

    # Message to return on POST Endpoint (will be replaced depending on validity of request)
    returnString = 'Invalid request'

    # returns true or false
    if checkValidJson(request.data):

        customerID, tagID, userID, remoteIP, timestamp = checkValidJson(request.data)

        returnString = 'customerID: ' + str(customerID) + '\n tagID: ' +  str(tagID) + '\n userID: ' +  str(userID) + '\n remoteIP: ' +  str(remoteIP) + '\n timestamp: ' +  str(timestamp)

        # Open database
        connection = sqlite3.connect('database.db')

        cur = connection.cursor()

        # Check IP
        try:
            ip = remoteIP.replace('.', '')
            ip = int(ip)
        except:
            returnString = 'Incorrect IP!'
            # TODO: exit and return invlaid request


        # Check if IP is blacklisted
        ip_blacklist = cur.execute('SELECT * FROM ip_blacklist').fetchall()

        for ip_bl in ip_blacklist:
            if ip_bl[0] == ip:
                returnString = 'Blacklisted IP!'
                # TODO: exit and return invlaid request


        # Check if username contains blacklisted user agent
        ua_blacklist = cur.execute('SELECT * FROM ua_blacklist').fetchall()     

        for ua in ua_blacklist:
            if ua[0] in userID:
                returnString = 'Blacklisted User Agent!'
                # TODO: exit and return invlaid request


        # Check if customer exists and is active
        try:
            customerActivity = cur.execute('SELECT active FROM customer WHERE id = ?', (customerID,)).fetchall()

            if customerActivity[0][0] == 0:
                returnString = 'Customer inactive!'
                # TODO: exit and return invlaid request

        except:
            returnString = 'Customer not in the database!'
            # TODO: exit and return invlaid request

        connection.close()


        process_request(customerID, tagID, userID, remoteIP, timestamp)



    return returnString




if __name__ == '__main__':

    '''Create global dictionaries storing total and invalid request counts for every user'''

    # Save customer IDs from database to a list
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()

    customer_ids_result = cur.execute('SELECT id FROM customer').fetchall()
    customer_ids = list(map(lambda x: x[0], customer_ids_result))

    connection.close()

    # Start total and invalid request count dictionaries to a manager to keep track of requests
    manager = Manager()
    total_request_count = manager.dict({i: 0 for i in customer_ids})
    invalid_request_count = manager.dict({i: 0 for i in customer_ids})


    '''Start app'''

    app.run(debug = True, port=5000)