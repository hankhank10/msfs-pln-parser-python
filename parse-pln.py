import xmltodict
import json
import secrets
import os
from pathlib import Path

from flask import Flask, jsonify, request, render_template

def OpenFile(filename):
    with open (filename, 'r') as xmlfile:
        xml_string = xmlfile.read()

    xml_string = xml_string.replace('°','')

    pln_dictionary = xmltodict.parse(xml_string)
    return pln_dictionary


def FixWaypoints(pln_dictionary):

    for waypoint in pln_dictionary['SimBase.Document']['FlightPlan.FlightPlan']['ATCWaypoint']:

        # Split into constituent parts
        waypoint['Latitude'] = waypoint['WorldPosition'].split(",")[0]
        waypoint['Longitude'] = waypoint['WorldPosition'].split(",")[1]
        waypoint['Altitude'] = waypoint['WorldPosition'].split(",")[2]
        
        # Tidy altitude
        waypoint['Altitude'] = float(waypoint['Altitude'])

        # Work out latitude
        latitude_direction = waypoint['Latitude'][0]
        rest_of_latitude = waypoint['Latitude'][1:]
        
        latitude_degrees = rest_of_latitude.split(" ")[0]
        latitude_minutes = rest_of_latitude.split(" ")[1]
        latitude_seconds = rest_of_latitude.split(" ")[2]

        latitude_minutes = latitude_minutes.split("'")[0]
        latitude_seconds = latitude_seconds.split('"')[0]

        latitude_degrees = int(latitude_degrees)
        latitude_minutes = int(latitude_minutes)
        latitude_seconds = float(latitude_seconds)

        latitude_decimal = latitude_degrees + (latitude_minutes/60) + (latitude_seconds/3600)
        print (str(latitude_degrees), str(latitude_minutes), str(latitude_seconds), ">", str(latitude_decimal))

        if latitude_direction == "S":
            latitude_decimal = -latitude_decimal
        waypoint['DecimalLatitude'] = latitude_decimal

        # Work out longitude
        longitude_direction = waypoint['Longitude'][0]
        rest_of_longitude = waypoint['Longitude'][1:]
        
        longitude_degrees = rest_of_longitude.split(" ")[0]
        longitude_minutes = rest_of_longitude.split(" ")[1]
        longitude_seconds = rest_of_longitude.split(" ")[2]

        longitude_minutes = longitude_minutes.split("'")[0]
        longitude_seconds = longitude_seconds.split('"')[0]

        longitude_degrees = int(longitude_degrees)
        longitude_minutes = int(longitude_minutes)
        longitude_seconds = float(longitude_seconds)

        longitude_decimal = longitude_degrees + (longitude_minutes/60) + (longitude_seconds/3600)
        print (str(longitude_degrees), str(longitude_minutes), str(longitude_seconds), ">", str(longitude_decimal))

        if longitude_direction == "W":
            longitude_decimal = -longitude_decimal
        waypoint['DecimalLongitude'] = longitude_decimal

    return pln_dictionary


def SaveFile(filename, pln_dictionary):
    with open (filename, 'w') as jsonfile:
        json.dump(pln_dictionary['SimBase.Document']['FlightPlan.FlightPlan'], jsonfile, indent=4)


#new_route = OpenFile('sample.pln')
#fixed_route = FixWaypoints(new_route)
#print (json.dumps(fixed_route))


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = "adsfdgkjwrkj7778jgjjhhqyqpp98876688767ayfyyf"

@app.route('/upload', methods=['GET', 'POST'])
def receive_upload():
    
    if request.method == "GET":
        return render_template('upload.html')


    if request.method == "POST":
        
        if 'file' not in request.files:
            return "No file uploaded"
        
        temporary_filename = secrets.token_urlsafe(25)

        file = request.files['file']
        extension = Path(file.filename).suffix

        if extension != ".pln":
            return "Please upload a .PLN file"

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], temporary_filename))

        new_route = OpenFile('/static/uploads/temporary_filename')
        fixed_route = FixWaypoints(new_route)
        return (jsonify(fixed_route))


@app.route('/')
def get_json():
    new_route = OpenFile('sample.pln')
    fixed_route = FixWaypoints(new_route)
    
    return (jsonify(fixed_route))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11046, debug=True)