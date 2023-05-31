from flask import Flask, jsonify
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd

# Create the engine
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# Create a Flask app
app = Flask(__name__)

# Define the home route
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Retrieve the most recent date from the database
    most_recent_date = engine.execute("SELECT MAX(date) FROM measurement").scalar()

    # Calculate the date one year ago from the most recent date
    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)

    # Perform a query to retrieve the data and precipitation scores
    query = f"SELECT date, prcp FROM measurement WHERE date >= '{one_year_ago.date()}'"
    results = engine.execute(query).fetchall()

    # Create a dictionary to store the date and precipitation data
    precipitation_data = {}
    for result in results:
        precipitation_data[result[0]] = result[1]

    # Return the precipitation data as JSON
    return jsonify(precipitation_data)


# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Perform a query to retrieve the station data
    query = "SELECT station FROM station"
    results = engine.execute(query).fetchall()

    # Create a list of station names
    station_list = [station[0] for station in results]

    return jsonify(station_list)

# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    # Perform a query to retrieve the last 12 months of temperature observation data for the specified station
    query = """
            SELECT tobs
            FROM measurement
            WHERE station = 'USC00519281' AND date >= (SELECT DATE(MAX(date), '-12 month') FROM measurement)
            """
    results = engine.execute(query).fetchall()

    # Create a list to store the temperature observations
    temperature_list = []
    for result in results:
        temperature_list.append(result[0])

    # Return the temperature observations as JSON
    return jsonify(temperature_list)


# Define the start and start-end date route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    """Return a JSON list of the minimum, average, and maximum temperature for the specified date range."""
    # Perform a query to calculate the temperature statistics
    if end:
        query = f"""
                SELECT MIN(tobs) AS min_temp, AVG(tobs) AS avg_temp, MAX(tobs) AS max_temp
                FROM measurement
                WHERE date BETWEEN :start_date AND :end_date
                """
        results = engine.execute(query, start_date=start, end_date=end).fetchone()
    else:
        query = f"""
                SELECT MIN(tobs) AS min_temp, AVG(tobs) AS avg_temp, MAX(tobs) AS max_temp
                FROM measurement
                WHERE date >= :start_date
                """
        results = engine.execute(query, start_date=start).fetchone()

    # Extract the temperature statistics
    min_temp = results.min_temp
    avg_temp = results.avg_temp
    max_temp = results.max_temp

    return jsonify({"min_temp": min_temp, "avg_temp": avg_temp, "max_temp": max_temp})

