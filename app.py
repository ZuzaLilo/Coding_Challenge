from flask import Flask, request
import sqlite3, json
from multiprocessing import Manager

import time, atexit, datetime
from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime, timedelta, date
from dateutil import tz


app = Flask(__name__)

def create_hourly_stats():
    print("\n")
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

    time_now = time.time()

    connection = sqlite3.connect('database.db')
    cur = connection.cursor()

    print("----total_request_count-----")
    print(total_request_count)
    print("----invalid_request_count-----")
    print(invalid_request_count)

    for client_id, req_count in total_request_count.items():
        cur.execute('INSERT INTO hourly_stats (customer_id, time, request_count, invalid_count) VALUES (?, ?, ?, ?)', (client_id, time_now, req_count, invalid_request_count[client_id]))
        
        # Empty statistics after inserting to database
        total_request_count[client_id] = 0
        invalid_request_count[client_id] = 0

    connection.commit()
    connection.close()


@app.before_first_request
def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=create_hourly_stats, trigger="interval", seconds=20)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


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
            invalid_request_count[customerID] += 1
            # TODO: exit


        # Check if IP is blacklisted
        ip_blacklist = cur.execute('SELECT * FROM ip_blacklist').fetchall()

        for ip_bl in ip_blacklist:
            if ip_bl[0] == ip:
                returnString = 'Blacklisted IP!'
                invalid_request_count[customerID] += 1
                # TODO: exit


        # Check if username contains blacklisted user agent
        ua_blacklist = cur.execute('SELECT * FROM ua_blacklist').fetchall()     

        for ua in ua_blacklist:
            if ua[0] in userID:
                returnString = 'Blacklisted User Agent!'
                invalid_request_count[customerID] += 1
                # TODO: exit


        # Check if customer exists and is active
        try:
            customerActivity = cur.execute('SELECT active FROM customer WHERE id = ?', (customerID,)).fetchall()

            if customerActivity[0][0] == 0:
                returnString = 'Customer inactive!'
                invalid_request_count[customerID] += 1
                # TODO: exit

        except:
            returnString = 'Customer not in the database, cannot assign count request to customer!'
            # TODO: exit

        connection.close()


        process_request(customerID, tagID, userID, remoteIP, timestamp)
    
    else:
        # Message to return on POST Endpoint
        returnString = 'Invalid request'

        try:
            invalid_request_count[customer_id] += 1
        except:
            print("Can't count request: can't find customer id!")


    return returnString



@app.route('/stats', methods = ['GET'])
def stats():

    # Get date parameters from request
    day = request.args.get('day')
    month = request.args.get('month')
    year = request.args.get('year')

    customer_id = request.args.get('customer_id')

    if day and month and year:

        try:
            day = int(request.args.get('day'))
            month = int(request.args.get('month'))
            year = int(request.args.get('year'))
        except:
            return "Date arguments must be numeric!"

        # Create datetime object for day start
        get_day_start = datetime(year, month, day, tzinfo=tz.tzutc())
        # Add a day difference to create end day object
        get_day_end = get_day_start + timedelta(1)

        # Convert to timestamps
        day_start_timestamp = get_day_start.timestamp()
        day_end_timestamp = get_day_end.timestamp()

        # Sum requests between start and end timestamps from database
        connection = sqlite3.connect('database.db')
        cur = connection.cursor()

        total_requests_in_day = cur.execute('SELECT SUM(request_count) FROM hourly_stats WHERE time BETWEEN ? AND ?', (day_start_timestamp, day_end_timestamp)).fetchall()

        connection.close()

        if customer_id:

            try:
                connection = sqlite3.connect('database.db')
                cur = connection.cursor()

                requests_per_customer = cur.execute('SELECT SUM(request_count), SUM(invalid_count) FROM hourly_stats WHERE (time BETWEEN ? AND ?) AND customer_id = ?', (day_start_timestamp, day_end_timestamp, customer_id)).fetchall()

                connection.close()

                if requests_per_customer[0][0] != None:
                    return "Requests on " + str(get_day_start.date()) + " for customer with id " + str(customer_id) + ": Total requests: " + str(requests_per_customer[0][0]) + ", Invalid requests: " + str(requests_per_customer[0][1])
                else: 
                    return "Wrong customer ID!"
            except:
                return "Failed to fetch results from database!"
            


        return "Total number of requests on " + str(get_day_start.date()) + " is: " + str(total_requests_in_day[0][0] if total_requests_in_day[0][0]!= None else 0)

    else:   
        # If any of arguments not provided or arguments not numeric
        
        # Get today's date
        current_day = date.today()

        return '''Please provide date arguments: day, month and year to the request (in numbers), 
                \nFor today use: http://127.0.0.1:5000/stats?day={}&month={}&year={}'''.format(current_day.day, current_day.month, current_day.year)

    




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