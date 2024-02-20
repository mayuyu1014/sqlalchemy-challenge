# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import numpy as np
#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate(yyyy-mm-dd)<br/>"
        f"/api/v1.0/startdate(yyyy-mm-dd)/enddate(yyyy-mm-dd)"
        )   

#route to display precipitation as date:prcp pairs 
@app.route("/api/v1.0/precipitation")
def prcp():
    # Create a session
    session = Session(engine)

    #copy the query that gets all the data from last year from jupyter notebook
    measurement_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').order_by(Measurement.date).all()

    #close the session
    session.close()

    #empty list to catch dict data
    precipitation_data = []
    #save data in a dict format and move into a list
    for date, prcp in measurement_data:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        precipitation_data.append(precipitation_dict)
    
    #return jsonified list of data
    return jsonify(precipitation_data)

#route to display all stations
@app.route("/api/v1.0/stations")
def station():
    # Create our session 
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all stations data
    stations = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    #close the session
    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for id, station, name, lat, lon, ele in stations:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = lat
        station_dict["longitude"] = lon
        station_dict["elevation"] = ele
        all_stations.append(station_dict)

    return jsonify(all_stations)

#route to display dates and temperature observations of the most-active station for the previous year of data
@app.route("/api/v1.0/tobs")
def most_active():
    # Create our session 
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query copied from jupyter notebook to avoid repeated work
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= '2016-08-23').order_by(Measurement.date).all()

    #close the session
    session.close()

    #empty list to catch dict data
    tobs_data = []
    #save data in a dict format and move into a list
    for date, tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature Observed"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

#create a pointer to select the data we want, avoid repeative tasks
sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]

#create a function to save query date in a dict format and put into a list, avoid repeative tasks
def display(str, result):
    #initialize the list with a customized message
    data = [str]
    #save data in a dict format and move into a list
    for min, max, avg in result:
        my_dict = {}
        my_dict["Min Temperature"] = min
        my_dict["Max Temperature"] = max
        my_dict["Mean Temperature"] = np.round(avg, 1)
        data.append(my_dict)

    return data

@app.route("/api/v1.0/api/v1.0/startdate(yyyy-mm-dd)/<start_date>")
def startdate(start_date):
        
    # Create our session 
    session = Session(engine)

    #check if start date is valid
    if session.query(Measurement.date).filter(Measurement.date == start_date).first() is None:
        session.close()
        return "Sorry the input date is out of range, the ealiest date is 2010-10-01"
    
    # Query copied from jupyter notebook to avoid repeated work
    results = session.query(*sel).filter(Measurement.date >= start_date).all()
    #close the session
    session.close()
    #customize message
    message = f"min, max, and mean of the temperatured observed since {start_date}"
    all_data = display(message, results)
    return jsonify(all_data)

@app.route("/api/v1.0/api/v1.0/startdate(yyyy-mm-dd)/<start_date>/enddate(yyyy-mm-dd)/<end_date>")
def startenddate(start_date, end_date):
    # Create our session 
    session = Session(engine)

    #check start date
    if session.query(Measurement.date).filter(Measurement.date == start_date).first() is None:
        session.close()
        return "Sorry the input start date is out of range, the ealiest date is 2010-10-01"
    #check end date
    if session.query(Measurement.date).filter(Measurement.date == end_date).first() is None:
        session.close()
        return "Sorry the input end date is out of range, the latest date is 2017-08-23"

    # Query copied from jupyter notebook to avoid repeated work
    results = session.query(*sel).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).all()

    #close the session
    session.close()

     #customize message
    message = f"min, max, and mean of the temperatured observed between {start_date} and {end_date}"
    all_data = display(message, results)

    return jsonify(all_data)

#################################################
# Run the app
#################################################
if __name__ == '__main__':
    app.run(debug=True)