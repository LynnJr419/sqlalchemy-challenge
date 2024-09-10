# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///D:/sqlalchemy-challenge/Surfsup/Resources/hawaii.sqlite")



# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).\
        order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into dictionary
    p_dict = dict(precipitation)
    return jsonify(p_dict)

@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(Station.id, Station.station).all()

    session.close()

    all_stations = []
    for id, name in stations:
        station_dict = {}
        station_dict["Station"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    # LIST - active_stations[(Station, Count)]
    most_active_station = active_stations[0][0]
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == most_active_station).\
            filter(Measurement.date >= last_year).all()

    session.close()

    t_dict = dict(temperature_data)
    return jsonify(t_dict)

@app.route("/api/v1.0/<start>")
def start_date(start):

    temperature_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    all_temperatures = []
    for tmin, tmax, tavg in temperature_data:
        temperature_dict = {}
        temperature_dict["Min"] = tmin
        temperature_dict["Max"] = tmax
        temperature_dict["Avg"] = tavg
        all_temperatures.append(temperature_dict)

    return jsonify(all_temperatures)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    temperature_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()
    
    all_temperatures = []
    for min, max, avg in temperature_data:
        temperature_dict = {}
        temperature_dict["Min"] = min
        temperature_dict["Max"] = max
        temperature_dict["Avg"] = avg
        all_temperatures.append(temperature_dict)

    return jsonify(all_temperatures)

if __name__ == '__main__':
    app.run(debug=True)