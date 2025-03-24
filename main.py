from flask import Flask, jsonify, request
import psutil
import cpuinfo
from uptime import uptime

app = Flask(__name__)

SECRET_KEY = "uuguigi"
PORT = 80

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "ALIVE"})

@app.route('/stats', methods=['GET'])
def stats():
    # Check for secret key in query parameters
    secret = request.args.get('key')
    if secret != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # Gather system statistics
    up = uptime()
    cpu = cpuinfo.get_cpu_info()["brand_raw"]  # Get CPU model
    threads = cpuinfo.get_cpu_info()["count"]  # Get number of threads
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = round(psutil.virtual_memory().used / 1_000_000_000, 2)
    total_ram = round(psutil.virtual_memory().total / 1_000_000_000, 2)
    swap_usage = round(psutil.swap_memory().used / 1_000_000_000, 2)
    total_swap = round(psutil.swap_memory().total / 1_000_000_000, 2)
    disk_usage = round(psutil.disk_usage('/').used / 1_000_000_000, 2)
    total_disk = round(psutil.disk_usage('/').total / 1_000_000_000, 2)

    # Prepare response
    response = {
        "cpu": {
            "model": cpu,
            "threads": threads,
            "usage": cpu_usage
        },
        "ram": {
            "used": ram_usage,
            "total": total_ram
        },
        "swap": {
            "used": swap_usage,
            "total": total_swap
        },
        "disk": {
            "used": disk_usage,
            "total": total_disk
        },
        "uptime": up
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(port=PORT)
