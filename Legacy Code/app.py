# app.py
import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from location_finder_code import LocationFinder

app = Flask(__name__)

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

if not API_KEY:
    raise ValueError("Google Maps API key not found! Please set it in the .env file.")

finder = LocationFinder(API_KEY)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        region = request.form.get('region')
        location_types = request.form.get('location_types')
        
        # Split location types by comma and strip whitespace
        location_types = [lt.strip() for lt in location_types.split(',') if lt.strip()]
        
        if not region:
            error = "Please enter a region."
            return render_template('index.html', error=error)
        
        if len(location_types) < 2:
            error = "Please enter at least 2 location types."
            return render_template('index.html', error=error)
        
        try:
            pairs = finder.find_closest_locations(region, location_types)
            return render_template('index.html', pairs=pairs, region=region, location_types=location_types)
        except Exception as e:
            error = f"An error occurred: {str(e)}"
            return render_template('index.html', error=error)
    
    return render_template('index.html')

if __name__ == '__main__':
    # For production, it's better to use a WSGI server like Gunicorn
    # Example: gunicorn app:app
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))