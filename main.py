import os
import hmac
from flask import Flask, jsonify, request
import psutil
import cpuinfo
from uptime import uptime

app = Flask(__name__)

# --- CONFIGURATION ---
# SECRET: Loaded from environment variable, with your preferred default fallback
SECRET_KEY = os.environ.get("API_SECRET_KEY", "uuguigi")
PORT = int(os.environ.get("PORT", 80))

# CONSTANT: Define GiB conversion for cleaner math
GB = 1024 ** 3 

# --- CACHE ---
# Gather static hardware info on startup so it doesn't bottleneck requests
print("Gathering static CPU info (this takes a moment)...")
_cpu_data = cpuinfo.get_cpu_info()
CPU_MODEL = _cpu_data.get("brand_raw", "Unknown CPU")
CPU_THREADS = _cpu_data.get("count", psutil.cpu_count(logical=True))


# --- ROUTES ---
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "ALIVE"})

@app.route('/stats', methods=['GET'])
def stats():
    # SECURITY: Using URL parameters as requested
    provided_key = request.args.get('key')
    
    # Use hmac.compare_digest to prevent timing attacks when checking the password
    if not provided_key or not hmac.compare_digest(provided_key, SECRET_KEY):
        return jsonify({"error": "Unauthorized"}), 401

    # Gather LIVE system statistics
    up = uptime()
    
    # PERFORMANCE: Lowered interval to 0.1s so the API doesn't freeze for a full second
    cpu_usage = psutil.cpu_percent(interval=0.1) 
    
    v_mem = psutil.virtual_memory()
    s_mem = psutil.swap_memory()
    disk = psutil.disk_usage('/')

    # Prepare response
    response = {
        "cpu": {
            "model": CPU_MODEL,       # Cached
            "threads": CPU_THREADS,   # Cached
            "usage": cpu_usage        # Live
        },
        "ram": {
            "used": round(v_mem.used / GB, 2),
            "total": round(v_mem.total / GB, 2)
        },
        "swap": {
            "used": round(s_mem.used / GB, 2),
            "total": round(s_mem.total / GB, 2)
        },
        "disk": {
            "used": round(disk.used / GB, 2),
            "total": round(disk.total / GB, 2)
        },
        "uptime": up
    }

    return jsonify(response)


if __name__ == '__main__':
    # Running on 0.0.0.0 allows it to be accessed from other machines on your network
    app.run(host='0.0.0.0', port=PORT)
