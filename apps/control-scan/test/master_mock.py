#!/usr/bin/python3
#
# Simple web server to mockup the master controller service.
#

from flask import Flask, request

app = Flask(__name__)

@app.route('/station/<int:station_id>', methods=['GET', 'POST', 'PUT'])
def station_update(station_id):
    input = request.args.get('analog_values')
    print("Station ", station_id, "reports: ", input)
    return "Success"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int("6000"))


