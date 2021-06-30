import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def index():
    return(f"Welcome to the Hawaii Climate API!<br>"
    f"Available routes: <br>"
    f"/api/v1.0/precipitation <br>"
    f"/api/v1.0/stations <br>"
    f"/api/v1.0/tobs <br>"
    f"/api/v1.0/start <br>"
    f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    # Latest_date = session.query(func.max(Measurement.date)).first()
    # year = Latest_date.strftime("%Y")
    # month = Latest_date.strftime("%-m")
    # day = Latest_date.strftime("%d")
    # print(month)
    # Calculate the date 1 year ago from the last data point in the database
    previousyr_date = dt.date(2017,8,23)-dt.timedelta(days=365)
      
    # Perform a query to retrieve the data and precipitation scores
    yr_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=previousyr_date).all()

    session.close()


    yr_data_dict = dict(yr_data)
    return(jsonify(yr_data_dict))
    


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = dict(session.query(Station.station, Station.name).all())
    session.close()
    return(jsonify(stations))

@app.route("/api/v1.0/tobs")
def active():
    session = Session(engine)
    active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.prcp).desc()).first()
    active_station_data = dict(session.query(Measurement.date, Measurement.tobs).filter(Measurement.station==active_station[0]).all())
    session.close()
    return(jsonify(active_station_data))

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")

def calc_temps(start=None, end=None):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    session = Session(engine)
    if not end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all() 

        temperature = list(np.ravel(results))

        return jsonify(temperature)

    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

        temperature = list(np.ravel(results))

        return jsonify(temperature)
    session.close()


if __name__== "__main__":
    app.run(debug=True)

