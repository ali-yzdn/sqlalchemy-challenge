from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy import join
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from dateutil.relativedelta import relativedelta
import datetime as dt
import numpy as np 

# Create engine and session to connect to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
session_linked = Session(engine)

# reflect an existing database into a new model
existing = automap_base()
# reflect the tables
existing.prepare(autoload_with=engine)

# Save references to each table
Measurement = existing.classes.measurement
Station = existing.classes.station

# Create the Flask app
app = Flask(__name__)

# Define routes
@app.route("/")
def homepage():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary by using date as the key and prcp as the value."""
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017,8,23) - relativedelta(years=1)
    # Perform a query to retrieve the data and precipitation scores
    date_and_percip_scores = session_linked.query(Measurement.date, Measurement.prcp, Station.name).\
               join(Station, Measurement.station == Station.station).\
                filter(Measurement.date >= one_year_ago).all()

    # Convert results to a dictionary
    prcp_data = [{"Date": date, "Precipitation": prcp, "Station": station_name} for date, prcp, station_name in date_and_percip_scores]
    
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    results = session_linked.query(Station.station).all()
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():

    session_linked = Session(engine)
    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    one_year_ago = dt.date(2017,8,23) - relativedelta(years=1)
    temp_most_active_data = session_linked.query(Measurement.date, Measurement.tobs, Station.name).\
               join(Station, Measurement.station == Station.station).\
        filter(Measurement.date >= one_year_ago, Measurement.station == 'USC00519281').all()
    
    # Convert the results to a list of dictionaries
    tobs_data = [{"Date": date, "Temperature": tobs, "Station": station_name} for date, tobs, station_name in temp_most_active_data]
    session_linked.close()
    
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session_linked = Session(engine)
    """Return TMIN, TAVG, and TMAX for all dates greater than or equal to the start date."""
    results = session_linked.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    
    # Convert results to a list of dictionaries
    temp_data = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]
    
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive."""
    results = session_linked.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert results to a list of dictionaries
    temp_data = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]
    session_linked.close()
    
    return jsonify(temp_data)

if __name__ == "__main__":
    app.run(debug=True)
