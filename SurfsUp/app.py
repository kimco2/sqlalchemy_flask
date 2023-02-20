import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#-------------------------------------------------
# Database Setup
#-------------------------------------------------
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

#-------------------------------------------------
#Route: precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Query for the date and precipitation data for the last year in the database
    precipitation_results = session.query(Measurement.date, Measurement.prcp).\
        filter(func.strftime(Measurement.date) >= ("2016-08-23")).all()
    session.close()

    # Save output to a dictionary
    precipitation_dictionary = {}
    for item in precipitation_results:
        key = item[0]
        val = item[1]
        precipitation_dictionary[key] = val
    
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
    filter(func.strftime(Measurement.date) >= ("2016-08-23")).all()
   
    # Close the session
    session.close()

    # Putting it into a list
    temps = list(np.ravel(waihee_station_temp))

    return jsonify(temps)


#-------------------------------------------------
#Route: dynamic_start
from datetime import datetime
# @app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start>")
def start(start):
    try:
        start = datetime.strptime(start, "%m%d%Y")
    except ValueError:
        raise ValueError("{'start'} is not in the required date format mmddYYYY")
  
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs),
    func.max(Measurement.tobs),
    func.avg(Measurement.tobs)]
    
    # Query the data to find min, max and average, filtering by the start date provided
    start_data = session.query(*sel).\
        filter((Measurement.date) >= (start)).all()
    session.close()

    start_list = list(np.ravel(start_data))

    return jsonify(start_list)


#-------------------------------------------------
# Route: dynamic start and end date

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_items(start, end='02022017'):



#----------------------------------------
#Route: dynamic start and end date
from datetime import datetime
@app.route("/api/v1.0/<start>/<end>")
def end(end):
    try:
        end = datetime.strptime(end, "%m%d%Y")
    except ValueError:
        raise ValueError("{'end'} is not in the required date format mmddYYY")
  
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs),
    func.max(Measurement.tobs),
    func.avg(Measurement.tobs)]
   
    end = session.query(*sel).\
        filter((Measurement.date) >= (start)).\
        filter((Measurement.date) <= (end)).all()
    session.close()

    end_list = list(np.ravel(end))

    return jsonify(end_list)


if __name__ == '__main__':
    app.run(debug=True)