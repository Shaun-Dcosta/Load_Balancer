import random
import string
import os
import redis 
from flask import Flask, request, jsonify, redirect, abort

app = Flask(__name__)

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379)) 

try:
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    redis_client.ping()
    print(f"Successfully connected to Redis at {redis_host}:{redis_port}")
except redis.exceptions.ConnectionError as e:
    print(f"Error connecting to Redis at {redis_host}:{redis_port}: {e}")
  
    redis_client = None 

POD_NAME = os.environ.get('HOSTNAME', 'unknown_pod') 

BASE_URL = os.environ.get('BASE_URL', "http://127.0.0.1:80/") 
SHORT_CODE_LENGTH = int(os.environ.get('SHORT_CODE_LENGTH', 6))

def generate_short_code(length=SHORT_CODE_LENGTH):
    """Generates a random short code and ensures it's unique in Redis."""
    characters = string.ascii_letters + string.digits
    if not redis_client:
         raise ConnectionError("Redis client not available") 

    while True:
        short_code = ''.join(random.choices(characters, k=length))
        if not redis_client.exists(short_code): 
            return short_code
        else:
            print(f"Code collision for {short_code}, generating another.")


@app.route('/', methods=['GET'])
def index():
    """Simple index route."""
    print(f"Pod {POD_NAME}: Handling GET / request")
    redis_status = "Connected" if redis_client and redis_client.ping() else "Disconnected"
    return jsonify({
        "message": "URL Shortener Service is running!",
        "pod_name": POD_NAME,
        "redis_status": redis_status
    }), 200

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Accepts long URL, generates short code, stores in Redis, returns short URL."""
    if not redis_client:
         abort(500, description="Redis service unavailable.") 
    
    if not request.json or 'url' not in request.json:
        abort(400, description="Bad Request: Missing 'url' in JSON payload.")

    long_url = request.json['url']
    if not long_url.startswith(('http://', 'https://')):
         long_url = 'http://' + long_url

    try:
        short_code = generate_short_code()
        redis_client.set(short_code, long_url) 

        short_url = BASE_URL + short_code
        print(f"Pod {POD_NAME}: Stored in Redis: {short_code} -> {long_url}") 
        return jsonify({"short_url": short_url}), 201
    except ConnectionError as e:
         print(f"Pod {POD_NAME}: Redis connection error during shorten: {e}")
         abort(500, description="Failed to store URL due to backend issue.")
    except Exception as e: 
         print(f"Pod {POD_NAME}: Error during shorten: {e}")
         abort(500, description="An internal error occurred.")


@app.route('/<short_code>', methods=['GET'])
def redirect_to_long_url(short_code):
    """Looks up short code in Redis and redirects."""
    if not redis_client:
         abort(500, description="Redis service unavailable.") 

    try:
        long_url = redis_client.get(short_code) 

        if long_url:
            print(f"Pod {POD_NAME}: Found in Redis & Redirecting {short_code} -> {long_url}") 
            return redirect(long_url, code=302)
        else:
            print(f"Pod {POD_NAME}: Code {short_code} NOT FOUND in Redis") 
            abort(404, description="Short URL not found.")
    except ConnectionError as e:
         print(f"Pod {POD_NAME}: Redis connection error during redirect: {e}")
         abort(500, description="Failed to retrieve URL due to backend issue.")
    except Exception as e: 
         print(f"Pod {POD_NAME}: Error during redirect: {e}")
         abort(500, description="An internal error occurred.")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 