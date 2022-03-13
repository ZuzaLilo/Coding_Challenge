from flask import Flask, request, jsonify
import sqlite3, json
from multiprocessing import Manager

import time, atexit, datetime
from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime, timedelta, date
from dateutil import tz


app = Flask(__name__)


# --- Empty stub function for valid requests --- 
def process_request(customerID, tagID, userID, remoteIP, timestamp):
    pass


# --- Create hourly stats ---
# 
# Insert to database values stored in:
# - total_request_count
# - invalid_request_count
def create_hourly_stats():

    # Get timestamp for current time
    time_now = time.time()

    # Connect to database
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()

    for client_id, req_count in total_request_count.items():
        cur.execute('INSERT INTO hourly_stats (customer_id, time, request_count, invalid_count) VALUES (?, ?, ?, ?)', (client_id, time_now, req_count, invalid_request_count[client_id]))
        
        # Empty statistics after inserting to database
        total_request_count[client_id] = 0
        invalid_request_count[client_id] = 0

    # Close connection to database
    connection.commit()
    connection.close()


# --- Check if received valid JSON ---
# 
# Returns customerID, tagID, userID, remoteIP, timestamp  
# or
# Returns False (if JSON is not valid)
def checkValidJson(data):
    try:
        json_data = json.loads(data)
        customerID, tagID, userID, remoteIP, timestamp = (json_data['customerID'], json_data['tagID'], json_data['userID'], json_data['remoteIP'], json_data['timestamp'])
        
        # Check datatypes
        if not (isinstance(customerID, int) and isinstance(tagID, int) and isinstance(userID, str) and isinstance(remoteIP, str) and isinstance(timestamp, int)):
            return False
        else:
            # If successfull and no errors then json is valid and pass extracted values
            return customerID, tagID, userID, remoteIP, timestamp

    except (ValueError, KeyError, TypeError):
        return False

# --- Before first request ---
# 
# Start scheduler for hourly statistics
@app.before_first_request
def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=create_hourly_stats, trigger="interval", minutes=60)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


# --- POST json data to this '/' endpoint ---
# 
# Example json:
# { 
#   "customerID":1,
#   "tagID":2,
#   "userID":"aaaaaaaa-bbbb-cccc-1111-222222222222",
#   "remoteIP":"123.234.56.78",
#   "timestamp":1500000000
# }
@app.route('/', methods = ['POST'])
def index():
    
    # First check if user provided "authentication" credentials
    try:
        #  Get customer_id from header parameters
        header_customer_id = int(request.headers.get('customer_id'))

        # Check if customer_id has been sourced from database
        try:
            # If yes, then increase total request count
            total_request_count[header_customer_id] += 1
        except:
            return "Customer not in the database!"

    except:
        return "To access this service please provide your credentials (customer_id) as a parameter!"


    if checkValidJson(request.data):

        # Get data if valid JSON
        customerID, tagID, userID, remoteIP, timestamp = checkValidJson(request.data)

        # Check if customerID in JSON matches customer_id provided in credentials
        if int(customerID) != header_customer_id:
            invalid_request_count[header_customer_id] += 1
            return "You can only make a request with customer_id that matches provided credentials"

        # Open database
        connection = sqlite3.connect('database.db')
        cur = connection.cursor()

        # Get blacklists from database
        ip_blacklist = cur.execute('SELECT * FROM ip_blacklist').fetchall()
        ua_blacklist = cur.execute('SELECT * FROM ua_blacklist').fetchall()
        
        # Get customer activity from database
        customerActivity = cur.execute('SELECT active FROM customer WHERE id = ?', (customerID,)).fetchall()

        connection.close()

        # Check if customer exists and is active
        if customerActivity[0][0] == 0:
            invalid_request_count[header_customer_id] += 1
            return 'Customer inactive!'


        # Check if IP correct
        try:
            ip = remoteIP.replace('.', '')
            ip = int(ip)
        except:
            invalid_request_count[header_customer_id] += 1
            return 'Incorrect IP!'


        # Check if IP is blacklisted
        for ip_bl in ip_blacklist:
            if ip_bl[0] == ip:
                invalid_request_count[header_customer_id] += 1
                return 'Blacklisted IP!'


        # Check if user agent contains blacklisted user agent
        header_user_agent = request.headers.get('User-Agent')

        for ua in ua_blacklist:
            if header_user_agent in ua:
                invalid_request_count[header_customer_id] += 1
                return 'Blacklisted User Agent!'

    else:
        invalid_request_count[header_customer_id] += 1

        # Message to return on POST Endpoint
        return 'Invalid JSON data'


    # If all above condictions passed then process request
    process_request(customerID, tagID, userID, remoteIP, timestamp)

    return 'Success'



@app.route('/stats', methods = ['GET'])
def stats():

    # Get parameters from request
    day = request.args.get('day')
    month = request.args.get('month')
    year = request.args.get('year')

    customer_id = request.args.get('customer_id')

    # For specific day statistics
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
        
        try: 
            # Connect to database
            connection = sqlite3.connect('database.db')
            cur = connection.cursor()

            # If customer id provided
            if customer_id:

                requests_per_customer = cur.execute('SELECT SUM(request_count), SUM(invalid_count) FROM hourly_stats WHERE (time BETWEEN ? AND ?) AND customer_id = ?', (day_start_timestamp, day_end_timestamp, customer_id)).fetchall()

                if requests_per_customer[0][0] == None:
                    connection.close()
                    return "Wrong customer ID!"
                else:
                    connection.close()
                    return "Total requests on " + str(get_day_start.date()) + " for customer with id " + str(customer_id) + ": Total requests: " + str(requests_per_customer[0][0]) + ", Invalid requests: " + str(requests_per_customer[0][1])

            # If no customer_id provided, get all results for day
            requests_in_day_per_customer = cur.execute('SELECT customer_id, SUM(request_count), SUM(invalid_count) FROM hourly_stats WHERE time BETWEEN ? AND ? GROUP BY customer_id ORDER BY customer_id DESC', (day_start_timestamp, day_end_timestamp)).fetchall()
      
            requests_in_day_total = cur.execute('SELECT SUM(request_count), SUM(invalid_count) FROM hourly_stats WHERE time BETWEEN ? AND ?', (day_start_timestamp, day_end_timestamp)).fetchall()
       
            connection.close()


            if requests_in_day_per_customer[0][0] == None:
                return "No results for this date!"    
            else: 
                # Create a dictionary with stats per customer
                result = {}

                for row in requests_in_day_per_customer:

                    customer = "customer_" + str(row[0])
                    result[customer] = {
                        'total_requests' : row[1],
                        'invalid_requests' : row[2]
                    }
                
                # Add the result for the total number per day 
                    result['total_number'] = {
                        'total_requests' : requests_in_day_total[0][0],
                        'invalid_requests' : requests_in_day_total[0][1]
                    }

                json_result = jsonify(result)
    
                return json_result
                
        except:
            return "Failed to fetch results from database!"

    else:   
        # If any of arguments not provided or arguments not numeric
        
        # Get today's date
        current_day = date.today()

        return '''Please provide date arguments: day, month and year to the request (in numbers), 
                \nFor today use: http://127.0.0.1:5000/stats?day={}&month={}&year={}'''.format(current_day.day, current_day.month, current_day.year)

    
@app.route('/customerStats', methods = ['GET'])
def customerStats():

    customer_id = request.args.get('customer_id')

    if customer_id:
        try:
            connection = sqlite3.connect('database.db')
            cur = connection.cursor()

            stats_per_customer = cur.execute('SELECT time, SUM(request_count), SUM(invalid_count) FROM hourly_stats WHERE customer_id = ? GROUP BY time ORDER BY time DESC', (customer_id)).fetchall()

            connection.close()

            result = {}

            for row in stats_per_customer:

                result_time = str(time.ctime(row[0]))
                result[result_time] = {
                    'total_requests' : row[1],
                    'invalid_requests' : row[2]
                }

            json_result = jsonify(result)

            if stats_per_customer[0][0] != None:
                return json_result
            else: 
                return "Wrong customer ID!"      

        except:
            return "Failed to fetch results from database!"

    else:
        return "Please provide a valid customer_id as a parameter!"



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