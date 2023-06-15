
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import requests
import time
import tkinter as tk


#Tesla API class
class TeslaAPI:
    TOKEN_FILENAME = "<file_path>" #Insert the file path to your token here
    API_URL = 'https://owner-api.teslamotors.com/api/1'
    HEADERS = {"content-type": "application/json; charset=UTF-8"}

    def __init__(self):
        with open(self.TOKEN_FILENAME, 'r') as f:
            self.token = json.load(f)
            self.headers = {**self.HEADERS, 'Authorization': 'Bearer {}'.format(self.token["access_token"])}

    def make_request(self, method, endpoint, data=None):
        response = requests.request(method, f'{self.API_URL}/{endpoint}', headers=self.headers, data=data)
        response.raise_for_status()
        return response.json()

    def get_vehicle(self):
        response = self.make_request('GET', 'vehicles')
        if "response" in response and response["response"]:
            return response["response"][0]
        else:
            return None

    #wake up the vehicle before sending a request
    def wake_up(self, vehicle_id):
        for _ in range(10):
            response = self.make_request('POST', f'vehicles/{vehicle_id}/wake_up')
            if response["response"]["state"] == 'online':
                break
            time.sleep(5)

    def get_vehicle_data(self, vehicle_id):
        return self.make_request('GET', f'vehicles/{vehicle_id}/vehicle_data')["response"]

    def start_climate(self, vehicle_id):
        return self.make_request('POST', f'vehicles/{vehicle_id}/command/auto_conditioning_start')["response"]

    def stop_climate(self, vehicle_id):
        return self.make_request('POST', f'vehicles/{vehicle_id}/command/auto_conditioning_stop')["response"]

app = Flask(__name__)
CORS(app)

tesla_api = TeslaAPI()

@app.route('/api/vehicle', methods=['GET'])
def get_vehicle_info():
    vehicle = tesla_api.get_vehicle()
    if vehicle:
        if vehicle["state"] != "offline":
            tesla_api.wake_up(vehicle["id"])
            vehicle_data = tesla_api.get_vehicle_data(vehicle["id"])
            return jsonify({
                "Vehicle": vehicle['display_name'],
                "Battery Level": vehicle_data['charge_state']['battery_level'],
                "Charging": vehicle_data['charge_state']['charging_state'],
                "Vehicle Status": vehicle['state']
            })
        else:
            return jsonify({"error": "Vehicle offline"}), 400
    else:
        return jsonify({"error": "No vehicle found"}), 400

@app.route('/api/climate/start', methods=['POST'])
def start_climate():
    vehicle = tesla_api.get_vehicle()
    
    if vehicle and vehicle["state"] != "offline":
        result = tesla_api.start_climate(vehicle["id"])
        return jsonify(result)
    else:
        return jsonify({"error": "Cannot start climate (Vehicle offline)"}), 400

@app.route('/api/climate/stop', methods=['POST'])
def stop_climate():
    vehicle = tesla_api.get_vehicle()
    
    if vehicle and vehicle["state"] != "offline":
        result = tesla_api.stop_climate(vehicle["id"])
        return jsonify(result)
    else:
        return jsonify({"error": "Cannot stop climate (Vehicle offline)"}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
