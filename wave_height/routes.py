from flask import render_template, current_app as app, request, redirect, url_for, flash, session, jsonify
import requests
from .models import User, Interaction
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
from authlib.integrations.flask_client import OAuth
from flask import render_template, redirect, url_for, session, flash
from . import db, oauth
from .models import User
from datetime import datetime
from collections import defaultdict
from g4f.client import Client


# Base API URLs
BASE_DAILY_API_URL = "https://barmmdrr.com/connect/gmarine_api?daily=wave_height_max,wave_direction_dominant,wave_period_max&timezone=Asia%2FSingapore"
BASE_HOURLY_API_URL = "https://barmmdrr.com/connect/gmarine_api?hourly=wave_height,wave_direction,wave_period&timezone=Asia%2FSingapore"

# Replace os.getenv calls with direct assignment
GOOGLE_CLIENT_ID = "153261727313-2k9a11664psddano14edajktmpue51b0.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

# # Configure OAuth Flow
# flow = Flow.from_client_config(
#     client_config={
#         "web": {
#             "client_id": GOOGLE_CLIENT_ID,
#             "client_secret": GOOGLE_CLIENT_SECRET,
#             "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#             "token_uri": "https://oauth2.googleapis.com/token",
#             "redirect_uris": ["http://127.0.0.1:5000/callback"]
#         }
#     },
#     scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
# )

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form.get('email')  # Get the email field from the form
        password = request.form['password']
        
        # Check if email is provided
        if not email:
            flash("Email is required.", "danger")
            return redirect(url_for('register'))

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists. Please log in or use a different email.", "danger")
            return redirect(url_for('register'))

        # Create and save the new user with the plain text password
        user = User(username=username, email=email)
        user.set_password(password)
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
    # Validate if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "User must be logged in to log interactions."}), 403

    user_id = session['user_id']
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    data = request.json.get('data')  # This holds the nested data structure

    # Ensure latitude, longitude, and data are present
    if latitude is None or longitude is None or data is None:
        return jsonify({"error": "Latitude, longitude, and data are required."}), 400

    # Extract the relevant parts of the nested JSON (e.g., hourly wave data)
    hourly_data = data.get("hourly_data", {})
    hourly = hourly_data.get("hourly", {})
    times = hourly.get("time", [])
    wave_heights = hourly.get("wave_height", [])
    wave_periods = hourly.get("wave_period", [])

    # Convert times to datetime objects
    times = [datetime.strptime(t, '%Y-%m-%dT%H:%M') for t in times]

    # Group data by day
    daily_data = defaultdict(lambda: {'wave_heights': [], 'wave_periods': []})
    for time, wave_height, wave_period in zip(times, wave_heights, wave_periods):
        day_key = time.date()  # Group by date (YYYY-MM-DD)
        daily_data[day_key]['wave_heights'].append(wave_height)
        daily_data[day_key]['wave_periods'].append(wave_period)

    # Calculate daily metrics
    daily_metrics = []
    for day, values in daily_data.items():
        max_wave_height = max(values['wave_heights'])
        min_wave_height = min(values['wave_heights'])
        max_wave_period = max(values['wave_periods'])
        min_wave_period = min(values['wave_periods'])
        daily_metrics.append({
            'day': day,
            'max_wave_height': max_wave_height,
            'min_wave_height': min_wave_height,
            'max_wave_period': max_wave_period,
            'min_wave_period': min_wave_period
        })

    # Save the interaction
    interaction = Interaction(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        data=data  # Store full JSON in the database for reference
    )
    db.session.add(interaction)
    db.session.commit()

    return jsonify({"status": "success", "message": "Interaction logged successfully.", "daily_metrics": daily_metrics}), 200

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

@app.route('/google_login')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/callback')
def google_callback():
    try:
        # Step 1: Retrieve the access token from Google
        token = oauth.google.authorize_access_token()
        print("Access Token:", token)  # Debugging line to check the token

        # Step 2: Use the access token to get user information
        user_info = oauth.google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
        print("User Info:", user_info)  # Debugging line to check user info response

        # Check if email is in the user_info
        email = user_info.get('email')
        if not email:
            flash("Google login failed: email not provided.", "danger")
            return redirect(url_for('login'))

        # Step 3: Handle the user login and session
        user = User.query.filter_by(email=email).first()
        if not user:
            # Register the user if not already in the database
            user = User(username=user_info['name'], email=email, password_hash=None)
            db.session.add(user)
            db.session.commit()

        # Log the user in by storing their ID in the session
        session['user_id'] = user.id
        flash("Successfully logged in with Google!", "success")
        return redirect(url_for('leaflet_map'))

    except Exception as e:
        print("Error during Google callback:", e)
        flash("Authentication failed.", "danger")
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    interactions = Interaction.query.filter_by(user_id=user_id).all()

    interaction_charts = []

    # Process each interaction to extract daily metrics
    for interaction in interactions:
        data = interaction.data
        hourly = data.get("hourly_data", {}).get("hourly", {})
        times = hourly.get("time", [])
        wave_heights = hourly.get("wave_height", [])
        wave_periods = hourly.get("wave_period", [])

        # Convert times to datetime objects
        times = [datetime.strptime(t, '%Y-%m-%dT%H:%M') for t in times]

        # Group data by day
        daily_data = defaultdict(lambda: {'wave_heights': [], 'wave_periods': []})
        for time, wave_height, wave_period in zip(times, wave_heights, wave_periods):
            day_key = time.date()  # Group by date (YYYY-MM-DD)
            daily_data[day_key]['wave_heights'].append(wave_height)
            daily_data[day_key]['wave_periods'].append(wave_period)

        # Create data for the chart for this interaction
        chart_data = []
        for day, values in daily_data.items():
            max_wave_height = max(values['wave_heights'])
            min_wave_height = min(values['wave_heights'])
            max_wave_period = max(values['wave_periods'])
            min_wave_period = min(values['wave_periods'])
            chart_data.append({
                'day': day.strftime('%Y-%m-%d'),
                'max_wave_height': max_wave_height,
                'min_wave_height': min_wave_height,
                'max_wave_period': max_wave_period,
                'min_wave_period': min_wave_period
            })

        interaction_charts.append({
            'interaction_id': interaction.id,
            'chart_data': chart_data
        })

    return render_template('dashboard.html',page="dashboard", interaction_charts=interaction_charts, interaction_count=len(interactions), current_date=datetime.now().strftime('%Y-%m-%d'))

@app.route('/analysis_tools', methods=['GET', 'POST'])
def analysis_tools():
    response = None
    if request.method == 'POST':
        # Get user input from form
        user_message = request.form.get('userMessage')

        # Run the GPT-4o Mini Analysis Tool
        client = Client()
        try:
            response_obj = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_message}]
            )
            response = response_obj.choices[0].message.content
        except Exception as e:
            response = f"Error while contacting GPT: {e}"

    return render_template('analysis_tools.html', response=response, page="analysis-tools")


@app.route('/run_analysis_tool', methods=['POST'])
def run_analysis_tool():
    # Assuming this is where you process data
    input_data = request.form.get('input_data')
    
    # Placeholder for processing logic
    result = f"Processing input: {input_data}"
    
    # You can modify this to return any response you need
    return jsonify({'status': 'success', 'result': result})
