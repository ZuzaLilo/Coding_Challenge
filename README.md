## Set up instructions

Install pipenv
```
pip install pipenv
```

Install dependencies and activate environment
```
pipenv install
pipenv shell
```

Initialize database and start app
```
python init_db.py
python app.py
```

To deactivate environment
```
exit
```

## Assumptions

- I found that I could not get a customer_id if the JSON file in POST request was corrupted. 
- However, I still wanted to to count these requests as invalid requests for specific customer, therefore: 
    - I simulated an "authentication" system where every user that is making a request needs to provide their credentials to access the system
    - To make a POST request, specify customer_id as key in headers (Example value: 1)
    
- I assumed that timestamp in JSON does not need to match current time
### Notes 

- I left JSON request and database as suggested in the example
- I left the application in debug mode

## How to use

1. For testing purposes (to get statistics more often) change interval in init_scheduler() 
    - For example to seconds=60

2. General JSON POST requests send to '/' endpoint 

    - NOTE: Need to provide a customer_id as a key in headers! (Example value: 1)

    - Send POST request with customer_id header to: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

    - Sample JSON: 
    ```
    {"customerID":1,"tagID":2,"userID":"aaaaaaaa-bbbb-cccc-1111-222222222222","remoteIP":"123.234.56.78","timestamp":1500000000}
    ```

3. For statistics there are 3 different types, all are GET request which require parameters and return JSON responses:

    1. Statistics per DAY: at '/dayStats' GET endpoint
        - Provide DATE details as parameters, for example: ?day=13&month=3&year=2022
        - Example: [http://127.0.0.1:5000/dayStats?day=13&month=3&year=2022](http://127.0.0.1:5000/dayStats?day=13&month=3&year=2022)
    
    2. ALL statistics per CUSTOMER: at '/customerStats' GET endpoint
        - Provide CUSTOMER id as parameter, for example: ?customer_id=1
        - Example: [http://127.0.0.1:5000/customerStats?customer_id=1](http://127.0.0.1:5000/customerStats?customer_id=1)
    
    3. Statistics per DAY and CUSTOMER: at '/customerDayStats' GET endpoint
        - Provide DATE and CUSTOMER details as parameters, for example: ?day=13&month=3&year=2022&customer_id=1
        - Example: [http://127.0.0.1:5000/customerDayStats?day=13&month=3&year=2022&customer_id=2](http://127.0.0.1:5000/customerDayStats?day=13&month=3&year=2022&customer_id=2)

### Online resources

1. Flask project documentation

    [https://flask.palletsprojects.com/en/2.0.x/](https://flask.palletsprojects.com/en/2.0.x/)


2. APScheduler documentation

    [https://apscheduler.readthedocs.io/en/3.x/userguide.html](https://apscheduler.readthedocs.io/en/3.x/userguide.html)

