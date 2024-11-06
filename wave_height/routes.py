from flask import render_template, current_app as app, request, redirect, url_for, flash, session, jsonify
import requests
from . import db
from .models import User, Interaction

# Base API URLs
BASE_DAILY_API_URL = "https://barmmdrr.com/connect/gmarine_api?daily=wave_height_max,wave_direction_dominant,wave_period_max&timezone=Asia%2FSingapore"
BASE_HOURLY_API_URL = "https://barmmdrr.com/connect/gmarine_api?hourly=wave_height,wave_direction,wave_period&timezone=Asia%2FSingapore"


@app.route('/')
def leaflet_map():
    latitude = request.args.get('latitude', '11.654916')
    longitude = request.args.get('longitude', '124.265899')

    # Build API URLs with the provided latitude and longitude
    info_api_url = f"https://barmmdrr.com/connect/gmarine_api?latitude={latitude}&longitude={longitude}&daily=wave_height_max,wave_direction_dominant,wave_period_max&timezone=Asia%2FSingapore"
    hourly_api_url = f"https://barmmdrr.com/connect/gmarine_api?latitude={latitude}&longitude={longitude}&hourly=wave_height,wave_direction,wave_period&timezone=Asia%2FSingapore"

    # Fetch data from the info API
    info_data = requests.get(info_api_url).json()
    
    # Fetch data from the hourly API
    hourly_data = requests.get(hourly_api_url).json()

    return render_template("leaflet_map.html", info_data=info_data, hourly_data=hourly_data, latitude=latitude, longitude=longitude, page='leaflet_map')

@app.route('/earth_map')
def earth_map():
    return render_template('earth_map.html', page='earth_map')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for('register'))

        # Create and save the new user with plain text password
        user = User(username=username)
        user.set_password(password)  # Save password directly
        db.session.add(user)
        db.session.commit()
        
        flash("User registered successfully! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html', page='register')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        # Verify the password directly
        if user and user.check_password(password):
            session['user_id'] = user.id  # Store user ID in session
            flash("Login successful!", "success")
            return redirect(url_for('leaflet_map'))
        
        flash("Invalid username or password.", "danger")

    return render_template('login.html', page='login')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/log_interaction', methods=['POST'])
def log_interaction():
    # if 'user_id' not in session:
    #     return jsonify({"error": "User must be logged in to log interactions."}), 403

    user_id = session['user_id']
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    data = request.json.get('data')  # This now holds all hourly data for the day

    # Ensure required data is present
    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and longitude are required."}), 400

    # Save the daily data in the database
    interaction = Interaction(user_id=user_id, latitude=latitude, longitude=longitude, data=data)
    db.session.add(interaction)
    db.session.commit()

    return jsonify({"status": "success", "message": "Interaction logged successfully."}), 200

@app.route('/fetch_data')
def fetch_data():
    # Get latitude and longitude from the request arguments
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if not latitude or not longitude:
        return jsonify({"error": "Latitude and longitude are required."}), 400

    # Build API URLs with the provided latitude and longitude
    info_api_url = f"https://barmmdrr.com/connect/gmarine_api?latitude={latitude}&longitude={longitude}&daily=wave_height_max,wave_direction_dominant,wave_period_max&timezone=Asia%2FSingapore"
    hourly_api_url = f"https://barmmdrr.com/connect/gmarine_api?latitude={latitude}&longitude={longitude}&hourly=wave_height,wave_direction,wave_period&timezone=Asia%2FSingapore"

    # Fetch data from the APIs
    try:
        info_data = requests.get(info_api_url).json()
        hourly_data = requests.get(hourly_api_url).json()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch data from APIs: {e}"}), 500

    # Return the data as JSON
    return jsonify({"info_data": info_data, "hourly_data": hourly_data})

