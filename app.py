# app.py

from flask import Flask, render_template, jsonify
import threading
import time
from server_node import get_sensor_data  # asumsi: fungsi get_sensor_data() ada di subscriber.py

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sensors')
def sensors_json():
    return jsonify({"sensors": get_sensor_data()})

def run_dashboard():
    app.run(debug=False, port=5000)

# Jalankan Flask di thread terpisah
threading.Thread(target=run_dashboard).start()