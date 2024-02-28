from flask import Flask, render_template, request, redirect, session ,flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy database for users, flights, and bookings
users = {
    'user1': {'password': 'password1'},
    'user2': {'password': 'password2'},
    'admin': {'password': 'admin_password'}
}

flights = {
    'FL001': {'name': 'Flight 1', 'date': '2024-02-26', 'time': '10:00', 'seats': 60},
    'FL002': {'name': 'Flight 2', 'date': '2024-02-27', 'time': '12:00', 'seats': 60},
    'FL003': {'name': 'Flight 3', 'date': '2024-02-26', 'time': '14:00', 'seats': 60}
}



bookings = {}

@app.route('/')
def index():
    return render_template('index.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if user exists and password is correct
        for user in users:
            if user['username'] == username and user['password'] == password:
                # User is authenticated, set session variable
                session['username'] = username
                session['logged_in'] = True
                flash('You are now logged in!', 'success')
                return redirect('/dashboard')
        # If user authentication fails, show error message
        flash('Invalid username or password. Please try again.', 'error')
        return redirect('/login')
    return render_template('login.html')

# Initialize list of users (You may want to use a database instead)
users = []

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if username already exists
        if any(user['username'] == username for user in users):
            flash('Username already exists! Please choose a different one.', 'error')
            return redirect('/signup')
        else:
            # Add new user to the list
            users.append({'username': username, 'password': password})
            flash('You have successfully signed up!', 'success')
            return redirect('/login')
    return render_template('signup.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        user_type = session['user_type']
        username = session['username']
        if user_type == 'admin':
            if request.method == 'POST':
                flight_id = request.form['flight_id']
                flight_name = request.form['flight_name']
                flight_date = request.form['flight_date']
                flight_time = request.form['flight_time']
                flights[flight_id] = {'flight_id':flight_id,'name': flight_name, 'date': flight_date, 'time': flight_time, 'seats': 60}
            return render_template('admin_dashboard.html', username=username, flights=flights)
        else:
            if request.method == 'POST':
                search_date = request.form['date']
                search_time = request.form['time']
                filtered_flights = [flight for flight in flights.values() if flight['date'] == search_date and flight['time'] == search_time]
                return render_template('user_dashboard.html', username=username, flights=filtered_flights, search_date=search_date, search_time=search_time)
            return render_template('user_dashboard.html', username=username, flights=flights)
    return redirect('/login')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/book/<flight_id>')
def book_flight(flight_id):
    if 'username' in session:
        username = session['username']
        if flight_id in flights:
            available_seats = flights[flight_id]['seats']
            if available_seats > 0:
                # Reduce available seats by 1 and book the flight
                flights[flight_id]['seats'] -= 1
                # Generate a unique booking ID (you can use a more robust method)
                booking_id = len(bookings) + 1
                bookings[booking_id] = {'username': username, 'flight_id': flight_id}
                return f"Booking successful! Your booking ID is {booking_id}"
            else:
                return f"Sorry, no seats available on this flight. Total seats available: {available_seats}"
        else:
            return "Invalid flight ID"
    return redirect('/login')


@app.route('/mybookings')
def my_bookings():
    if 'username' in session:
        username = session['username']
        user_bookings = [booking for booking in bookings.values() if booking['username'] == username]
        return render_template('my_bookings.html', bookings=user_bookings)
    return redirect('/login')

@app.route('/admin')
def admin():
    if 'username' in session and session['user_type'] == 'admin':
        return render_template('admin.html', flights=flights, bookings=bookings)
    return redirect('/login')

@app.route('/remove_flight/<flight_id>')
def remove_flight(flight_id):
    if 'username' in session and session['user_type'] == 'admin':
        if flight_id in flights:
            del flights[flight_id]
        # Remove bookings associated with the removed flight
        bookings_to_remove = [booking_id for booking_id, booking in bookings.items() if booking['flight_id'] == flight_id]
        for booking_id in bookings_to_remove:
            del bookings[booking_id]
        return redirect('/admin')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
