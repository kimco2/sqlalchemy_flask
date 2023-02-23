#-------------------------------------------------
# Dependencies
#-------------------------------------------------
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

from datetime import datetime

#-------------------------------------------------
# Database Setup
#-------------------------------------------------
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#-------------------------------------------------
# Flask Setup
#-------------------------------------------------
app = Flask(__name__)

#-------------------------------------------------
# Flask Routes
#-------------------------------------------------
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to this climate api for Hawaii<br/>"
        f"<br/>"   
        f"Available routes are:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"  
        f"/api/v1.0/start/end<br/>"  
        f"<br/>"
        f"If using the routes containing 'start' or 'end', please replace 'start' and 'end' with a date in the format ddmmYYYY <br/>" 
        f"<br/>"
        f"For example for the route '/api/v1.0/start'<br/>"
        f"/api/v1.0/28012016<br/>"
        f"<br/>"
        f"For example for the route '/api/v1.0/start/end'<br/>"
        f"/api/v1.0/28012016/28012017"
    )

#-------------------------------------------------
#Route: precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Query for the date and precipitation data for the last year in the database
    precipitation_results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-23").all()
    
    # Close the session
    session.close()

    # Save output to a dictionary
    precipitation_dictionary = {}
    for item in precipitation_results:
        key = item[0]
        value = item[1]
        precipitation_dictionary[key] = value
    
    return jsonify(precipitation_dictionary)


#-------------------------------------------------
## Route: stations
@app.route("/api/v1.0/stations")
def stations():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Query for all the stations
    station_results = session.query(Station.station).all()

    # Close the session
    session.close

    # Putting it into a list
    stations = list(np.ravel(station_results))
    
    # Returning the list in JSON format
    return jsonify(stations)

#-------------------------------------------------
#Route: tobs
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for all the temperatures for the active staton in the last 12 months
    waihee_station_temp = session.query(Measurement.tobs).\
    filter(Measurement.station == "USC00519281").\
    filter(Measurement.date >= "2016-08-23").all()
   
    # Close the session
    session.close()

    # Converting list of tuples into normal list
    temps = list(np.ravel(waihee_station_temp))

    # Returning the list in JSON format
    return jsonify(temps)
 
#-------------------------------------------------
# #Route: dynamic api start 
@app.route("/api/v1.0/<start>")
def stats_start(start):
    start = datetime.strptime(start, "%d%m%Y")

    # Defining part of the query to obtain minimum, maximum and average temperatures
    sel = [func.min(Measurement.tobs),
    func.max(Measurement.tobs),
    func.avg(Measurement.tobs)]

    # Create a session from Python to the DB
    session = Session(engine)

    # Running the query to get to obtain minimum, maximum and average temperatures
    temp_data = session.query(*sel).\
    filter(Measurement.date >= start).all()

    # Closing the session
    session.close()

    # Converting list of tuples into normal list and saving to a dictionary
    temp_list = list(np.ravel(temp_data))
    temp_dict = {
        "TMIN" : temp_list[0],
        "TMAX" : temp_list[1],
        "TAVG" : temp_list[2]
    }

    return jsonify(temp_dict)
 

#---------------------------
# #Route: dynamic api start and end
@app.route("/api/v1.0/<start>/<end>")
def stats_start_end(start, end):
    start = datetime.strptime(start, "%d%m%Y")
    end = datetime.strptime(end, "%d%m%Y")

    # Defining part of the query to obtain minimum, maximum and average temperatures
    sel = [func.min(Measurement.tobs),
    func.max(Measurement.tobs),
    func.avg(Measurement.tobs)]

    # Create a session from Python to the DB
    session = Session(engine)

    # Running the query to get to obtain minimum, maximum and average temperatures
    temp_data = session.query(*sel).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()

    # Closing the session
    session.close()

    # Converting list of tuples into normal list and saving to a dictionary
    temp_list = list(np.ravel(temp_data))
    temp_dict = {
        "TMIN" : temp_list[0],
        "TMAX" : temp_list[1],
        "TAVG" : temp_list[2]
    }

    return jsonify(temp_dict)

# Turning on the dubug mode
if __name__ == '__main__':
    app.run(debug=True)