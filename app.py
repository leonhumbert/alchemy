import numpy as np

import datetime as dt
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

############################
#Flask Setup - weather app
############################

app = Flask(__name__)

############################
# Flask Routes
############################

@app.route("/")

def home():
    return (f"Welcome to Surf's Up!<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"This is a list of available routes:<br/>"
       
            f"/api/v1.0/precipitation <br/>"
            f"/api/v1.0/stations <br/>"
            f"/api/v1.0/temperature <br/>"
            f"/api/v1.0/start <br/>"
            f"/api/v1.0/start/end <br/>"
            f"~ data available from 2010-01-01 to 2017-08-23 ~<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    last_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    # Get the first element
    last_date = last_date[0]
    # Calculates dates of last year of data points in the dataset revious year
    previous_year = dt.datetime.strptime(last_date,"%Y-%m-%d") - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = (session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.asc()).filter(Measurement.date>=previous_year).all())
    
    prcp_dict = {}
    
    for result in precipitation_data:
        prcp_dict[result[0]] = result[1]


    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Docstring
    """Return a JSON list of stations from the dataset."""
    #Query stations
    results_stations = session.query(Station.name).all()
    #Convert list of tuples into a list
    all_stations = list(np.ravel(results_stations))
    return jsonify(all_stations)


@app.route("/api/v1.0/temperature")
def temperature():
    
    #Query to retrieve the last 12 months of precipitation data 
    last_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    # Get the first element
    last_date = last_date[0]
    # Calculates dates of last year of data points in the dataset revious year
    previous_year = dt.datetime.strptime(last_date,"%Y-%m-%d") - dt.timedelta(days=365)
    # Query tobs
    tobs_data = (session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= previous_year).all())
    
    # Convert list of tuples into normal list
    tobs_list = list(tobs_data)

    return jsonify(tobs_list)

#function to calculate min, average and max temps between date ranges
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return (session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all())

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
    
def start_date(start, end=None):  
#get dates and use contional in case user inputs only start date

    if not end:
        end_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
        end = end_date[0]
    #gets results 
    temps = calc_temps (start, end)
    #create a list
    return_list = []
    #adds labels to each result
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)
    
if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    