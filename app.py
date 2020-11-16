from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext import automap
from sqlalchemy import inspect
from sqlalchemy import func
import numpy as np
from flask import Flask, jsonify
import datetime as dt

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap.automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def Welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs_most active stationbr/>"
        f"/api/v1.0/enter start date here<br/>"
        f"/api/v1.0/enterstart date here/enter end date here"
    )

@app.route("/api/v1.0/precipitation")
def Precipitation():
    session = Session(engine)
    date = session.query(func.max(Measurement.date)).first()

    year_ago = dt.datetime.strptime(date[0], '%Y-%m-%d')
    year_ago = dt.date(year_ago.year-1,year_ago.month,year_ago.day)

    prcp = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date >= year_ago).all()

    session.close()

    list_prcp = [{"Date": date, "Prcp": prcp} for date, prcp in prcp]

    return jsonify(list_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    total_stations = session.query(Station.station, Station.name).group_by(Station.station).all()
    
    session.close()

    list_stations = [{"Station": station, "Name": name} for station, name in total_stations]

    return jsonify(list_stations)

@app.route("/api/v1.0/tobs_MostActiveStation")
def tobs():
    session = Session(engine)
    active_stations = session.query(Station.station,Station.name, func.count(Measurement.prcp)).\
            filter(Station.station == Measurement.station).group_by(Station.name).\
            order_by((func.count(Measurement.prcp)).desc()).all()
    
    session.close()
    
    list_temps = [{"Date": date, "Temp Obs": tobs} for date, tobs in active_stations]

    return jsonify(list_temps)

@app.route("/api/v1.0/<start>")
def temp_stats_v1(start):
    session = Session(engine)
    start = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start)
    
    session.close()

    start_list = [{"Min Temp": tmin, "Max Temp": tmax, "Avg Temp": tavg} for tmin, tavg, tmax in start]
    
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_v2(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    session.close()

    result_list = [{"Min Temp": tmin, "Max Temp": tmax, "Avg Temp": tavg} for tmin, tavg, tmax in results]
    
    return jsonify(result_list)

if __name__ == "__main__":
    app.run(debug=True)