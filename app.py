from flask import Flask, request, jsonify, redirect
import redis
import random
import string

app = Flask(__name__)

# Connect to Redis (in-memory key-value store)
redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

def generate_short_id():
    """Generates a random 6-character short URL ID."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Shortens a given long URL."""
    data = request.get_json()

    if not data or "longUrl" not in data:
        return jsonify({"error": "Missing longUrl"}), 400

    long_url = data["longUrl"]
    short_id = generate_short_id()

    # Store in Redis
    redis_client.set(short_id, long_url)

    return jsonify({"shortUrl": f"http://localhost:5000/{short_id}"}), 201

@app.route('/<short_id>', methods=['GET'])
def redirect_url(short_id):
    """Redirects to the original URL."""
    long_url = redis_client.get(short_id)

    if long_url:
        return redirect(long_url)
    return jsonify({"error": "Short URL not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
