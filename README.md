# SET UP INSTRUCTIONS

Install pipenv
```
pip install pipenv
```

Install dependencies and run in a shell
```
pipenv install
pipenv shell
```

Initilasie database
```
python init_db.py
```

Start app
```
python app.py
```


# USAGE

### Assumptions

- I found that I could not get a customer_id if the JSON file in POST request was corrupted. However, I still wanted to to count these requests as invalid requests, therefore: 
    - I simulated an "authentication" system where every user that is making a request needs to provide their credentials in POST request header
- I left sample JSON request and database as suggested in the example

## How to use

1. General JSON POST requests send to '/' endpoint (NOTE: Need to provide a customer_id as a header! For example: 1)

    - Send POST request with customer_id header to: [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

    - Sample JSON: {"customerID":1,"tagID":2,"userID":"aaaaaaaa-bbbb-cccc-1111-222222222222","remoteIP":"123.234.56.78","timestamp":1500000000}

2. For statistics there are 3 different types:

    1. Statistics per day: at '/stats' endpoint
        - Provide DATE details as parameters, for example: ?day=13&month=3&year=2022
        - Example: [http://127.0.0.1:5000/stats?day=13&month=3&year=2022](http://127.0.0.1:5000/stats?day=13&month=3&year=2022).
    
    2. ALL statistics per customer: at '/customerStats' endpoint
        - Provide CUSTOMER id as parameter, for example: ?customer_id=1
        - Example: [http://127.0.0.1:5000/customerStats?customer_id=1](http://127.0.0.1:5000/customerStats?customer_id=1).
    
    3. Statistics per day and per customer: at '/stats' endpoint
        - Provide DATE and CUSTOMER details as parameters, for example: ?day=13&month=3&year=2022&customer_id=1
        - Example: [http://127.0.0.1:5000/stats?day=13&month=3&year=2022&customer_id=2](http://127.0.0.1:5000/stats?day=13&month=3&year=2022&customer_id=2).




