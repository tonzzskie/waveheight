from flask import render_template, current_app as app, request
import requests

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
