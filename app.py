import bigquery_wrapper
import collections
import json
import pymysql
import location_manager
import sys
import util


from datetime import datetime
from functools import wraps
from flask import Flask, jsonify, request,  render_template
from geopy.distance import geodesic

app = Flask(__name__)

# Load Configuration from Home Assistant
CONFIG = {}
with open("/data/options.json", "r") as file:
    CONFIG.update(json.load(file))

# Setup dependencies
locations = location_manager.LocationManager(
    CONFIG['mysql_host'], 
    CONFIG['mysql_user'], 
    CONFIG['mysql_password'], 
    CONFIG['mysql_db'])


@app.route("/")
def index():
    return render_template('ui.htm', google_maps_api_key=CONFIG.get("google_maps_api_key"))


@app.route("/data")
def get_data():
    try:
        response = jsonify({"data": locations.retrieve_location_data(CONFIG['entity_id'])})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Example calls: point_history?latitude=33.9774175&longitude=-118.4115714&threshold_miles=0.1&data_format=short
@app.route("/point_history")
def point_history():
    rows = locations.point_history(
        CONFIG['entity_id'], 
        float(request.args.get('latitude')), 
        float(request.args.get('longitude')),
        float(request.args.get('threshold_miles', default=0.25))
    )
    return list({util.to_local_full_format(row['timestamp']) for row in rows})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8099, debug=True)
