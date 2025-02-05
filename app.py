# Importing necessary libraries and modules
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
from flask_mysqldb import MySQL
import MySQLdb.cursors
from functools import wraps
import secrets
import sys
import datetime
import os 

# Initialize the Flask application
app = Flask(__name__)

# Configure MySQL database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'silverdawncoaches'

# Set the secret key for session management
app.secret_key = secrets.token_hex(16)

# Define the admin password
ADMIN_PASSWORD = "root"

# Initialize MySQL extension
mysql = MySQL(app)

@app.route('/')
def index():
    """
    Renders the main page of the application.
    """
    return render_template('main.html')

@app.route('/exit')
def exit_app():
    """
    Exits the application.
    """
    app.aborter(500) 

@app.route('/new_information')
def new_information():
    """
    Renders the new information page.
    """
    return render_template('new_information.html')

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    """
    Handles the addition of a new customer.
    If the request method is POST, it processes the form data and inserts a new customer into the database.
    If the request method is GET, it renders the form for adding a new customer.
    """
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['surname']
        email = request.form['email']
        address_line_1 = request.form['address_line_1']
        address_line_2 = request.form['address_line_2']
        city = request.form['city']
        postcode = request.form['postcode']
        phone_number = request.form['phone_number']
        special_notes = request.form['special_notes']

        # Insert data into the database
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO customer (first_name, last_name, email, address_line_1, address_line_2, city, postcode, phone_number, special_notes)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',  
                       (first_name, last_name, email, address_line_1, address_line_2, city, postcode, phone_number, special_notes))
        mysql.connection.commit()
        cursor.close()

        return render_template('add/customer.html', success=True)

    return render_template('add/customer.html')

@app.route('/add_trip', methods=['GET', 'POST'])

def add_trip():
    """
    Handles the addition of a new trip.
    If the request method is POST, it processes the form data and inserts a new trip into the database.
    If the request method is GET, it fetches existing destinations, coaches, and drivers to populate the form.
    """
    if request.method == 'POST':
        # Get form data
        destination_id = request.form['destination']
        coach_id = request.form['coach']
        driver_id = request.form['driver']
        trip_date = request.form['trip_date']

        # Insert data into the database
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO trip (destination_id, 
                       coach_id, driver_id, 
                       trip_date)
                          VALUES (%s, %s, %s, %s)''',
                       (destination_id, coach_id, 
                        driver_id, trip_date))
        mysql.connection.commit()
        cursor.close()

        return render_template('add/trip.html', success=True)

    # Fetch existing destinations, coaches, and drivers
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT destination_id, destination_name FROM destination')
    destinations = cursor.fetchall()
    cursor.execute('SELECT coach_id, coach_registration, num_of_seats FROM coach')
    coaches = cursor.fetchall()
    cursor.execute('SELECT driver_id, CONCAT(driver_first_name, " ", driver_last_name) AS name FROM driver')
    drivers = cursor.fetchall()
    cursor.close()

    return render_template('add/trip.html', destinations=destinations, coaches=coaches, drivers=drivers)

@app.route('/add_destination', methods=['GET', 'POST'])

def add_destination():
    """
    Handles the addition of a new destination.
    If the request method is POST, it processes the form data and inserts a new destination into the database.
    If the request method is GET, it renders the form for adding a new destination.
    """
    if request.method == 'POST':
        try:
            # Get form data
            destination_name = request.form['destination_name']
            destination_hotel = request.form['destination_hotel']
            destination_city = request.form['destination_city']
            destination_cost = request.form['destination_cost']
            number_of_days = request.form['number_of_days']

            # Insert data into the database
            cursor = mysql.connection.cursor()
            cursor.execute('''INSERT INTO destination (destination_name, destination_hotel, destination_city,
                           destination_cost, number_of_days)
                              VALUES (%s, %s, %s, %s, %s)''',
                           (destination_name, destination_hotel, destination_city, destination_cost, number_of_days))
            mysql.connection.commit()
            cursor.close()

            return render_template('add/destination.html', success=True)
        except Exception as e:
            return str(e), 500

    return render_template('add/destination.html')

@app.route('/add_driver', methods=['GET', 'POST'])

def add_driver():
    """
    Handles the addition of a new driver.
    If the request method is POST, it processes the form data and inserts a new driver into the database.
    If the request method is GET, it renders the form for adding a new driver.
    """
    if request.method == 'POST':
        # Get form data
        driver_firstname = request.form['first_name']
        driver_lastname = request.form['last_name']

        # Insert data into the database
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO driver (driver_first_name, driver_last_name)
                          VALUES (%s, %s)''',
                       (driver_firstname, driver_lastname))
        mysql.connection.commit()
        cursor.close()

        return render_template('add/driver.html', success=True)

    return render_template('add/driver.html')

@app.route('/add_coach', methods=['GET', 'POST'])

def add_coach():
    """
    Handles the addition of a new coach.
    If the request method is POST, it processes the form data and inserts a new coach into the database.
    If the request method is GET, it renders the form for adding a new coach.
    """
    if request.method == 'POST':
        # Get form data
        reg_number = request.form['reg_number']
        num_of_seats = request.form['seating_capacity']
        
        # Insert data into the database
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO coach (coach_registration, num_of_seats)
                          VALUES (%s, %s)''',
                       (reg_number, num_of_seats))
        mysql.connection.commit()
        cursor.close()

        return render_template('add/coach.html', success=True)

    return render_template('add/coach.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Handles the search functionality.
    If the request method is POST, it processes the form data to search within a selected table and column.
    If the request method is GET, it processes the query parameters to perform the search.
    Fetches the list of tables and columns dynamically from the database.
    Renders the search results on the search page.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()

    columns = []
    results = []
    selected_table = None
    selected_column = None

    if request.method == 'POST':
        selected_table = request.form['table']
        selected_column = request.form['column']
        search_value = request.form['search']
        
    elif request.method == 'GET':
        selected_table = request.args.get('table')
        selected_column = request.args.get('column')
        search_value = request.args.get('search')

    print(f"Selected Table: {selected_table}")
    print(f"Selected Column: {selected_column}")
    print(f"Search Value: {search_value}")

    if selected_table:
        cursor.execute(f"SHOW COLUMNS FROM {selected_table}")
        columns = [column['Field'] for column in cursor.fetchall()]

    if selected_table and selected_column:
        if search_value:
            if selected_column == '*':
                query = f"SELECT * FROM {selected_table} WHERE CONCAT_WS(' ', {', '.join(columns)}) LIKE %s"
                cursor.execute(query, (f"%{search_value}%",))
            else:
                query = f"SELECT {selected_column} FROM {selected_table} WHERE {selected_column} LIKE %s"
                cursor.execute(query, (f"%{search_value}%",))
        else:
            if selected_column == '*':
                query = f"SELECT * FROM {selected_table}"
            else:
                query = f"SELECT {selected_column} FROM {selected_table}"
            cursor.execute(query)
        
        results = cursor.fetchall()
        print(f"Query: {query}")
        print(f"Results: {results}")

    return render_template('search.html', tables=tables, columns=columns, 
                           results=results, selected_table=selected_table, 
                           selected_column=selected_column)

@app.route('/add_booking', methods=['GET', 'POST'])
def add_booking():
    """
    Handles the addition of a new booking.
    If the request method is POST, it processes the form data and inserts a new booking into the database.
    If the request method is GET, it fetches existing customers, destinations, and trips to populate the form.
    Renders the booking form and displays success or error messages based on the operation result.
    """
    # Fetch all necessary data for the form (used in both GET and POST)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get customers for dropdown
    cursor.execute('SELECT customer_id, CONCAT(first_name, " ", last_name) AS customer_name FROM customer')
    customers = cursor.fetchall()
    
    # Get destinations for potential filtering
    cursor.execute('SELECT destination_id, destination_name FROM destination')
    destinations = cursor.fetchall()
    
    # Get trips with seat information
    cursor.execute('''SELECT trip.trip_id, trip.destination_id, trip.trip_date, coach.num_of_seats 
                      FROM trip 
                      JOIN coach ON trip.coach_id = coach.coach_id''')
    trips = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        # Process form data
        trip_id = request.form['trip_date']
        customer_id = request.form['customer']
        special_notes = request.form.get('special_notes', '')
        num_people = int(request.form['num_people'])

        # Calculate booking cost
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT destination_cost FROM destination 
                          JOIN trip ON destination.destination_id = trip.destination_id 
                          WHERE trip.trip_id = %s''', (trip_id,))
        destination = cursor.fetchone()
        destination_cost = destination['destination_cost']
        booking_cost = num_people * destination_cost
        booking_date = datetime.datetime.now().strftime('%Y-%m-%d')

        # Insert booking
        try:
            cursor.execute('''INSERT INTO booking 
                            (trip_id, num_of_people, customer_id, booking_cost, special_request, booking_date)
                            VALUES (%s, %s, %s, %s, %s, %s)''',
                           (trip_id, num_people, customer_id, booking_cost, special_notes, booking_date))
            mysql.connection.commit()
            success = True
        except Exception as e:
            success = False
            print(f"Error: {e}")
        finally:
            cursor.close()

        return render_template('add/booking.html',
                               success=success,
                               customers=customers,
                               destinations=destinations,
                               trips=trips)

    # GET request - show empty form
    return render_template('add/booking.html',
                           customers=customers,
                           destinations=destinations,
                           trips=trips)


@app.route('/get_booked_seats')
def get_booked_seats():
    """
    Retrieves the number of available seats for a specific trip.
    This function fetches the trip ID from the request arguments, queries the database to calculate the number of available seats for the specified trip, and returns the result as a JSON response.
    Returns:
        JSON: A JSON object containing the number of available seats for the specified trip.
        The SQL query calculates the number of available seats for a specific trip by:
        1. Selecting the total number of seats for the coach associated with the trip.
        2. Subtracting the sum of the number of people booked for the trip (if any).
        3. Grouping the result by the total number of seats to ensure accurate calculation.
        4. Using a LEFT JOIN to include trips with no bookings, ensuring the availability is calculated correctly even if no bookings exist.
    """
    trip_id = request.args.get('trip_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT 
            c.num_of_seats - COALESCE(SUM(b.num_of_people), 0) AS seats_available,
            c.num_of_seats
        FROM 
            trip t
        JOIN 
            coach c ON t.coach_id = c.coach_id
        LEFT JOIN 
            booking b ON t.trip_id = b.trip_id
        WHERE 
            t.trip_id = %s
        GROUP BY 
            c.num_of_seats
    ''', (trip_id,))
    result = cursor.fetchone()
    cursor.close()

    seats_available = result['seats_available'] if result['seats_available'] is not None else 0
    num_of_seats = result['num_of_seats']
    return jsonify({'seats_available': seats_available, 'num_of_seats': num_of_seats})


if __name__ == "__main__":
    app.run(debug=True)