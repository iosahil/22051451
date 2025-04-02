from flask import Flask, jsonify
import requests
import statistics
import json

app = Flask(__name__)

WINDOW_SIZE = 10
window_state = []

BASE_URL = "http://20.244.56.144/evaluation-service"
TYPE_MAP = {
    'p': 'primes',
    'e': 'even',
    'f': 'fibo',
    'r': 'rand'
}


def load_access_token():
    try:
        with open('auth_token.json', 'r') as f:
            token_data = json.load(f)
            return token_data.get('access_token')
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading access token: {e}")
        return None


ACCESS_TOKEN = load_access_token()


@app.route('/numbers/<type_code>', methods=['GET'])
def get_numbers(type_code):
    global window_state

    endpoint = TYPE_MAP.get(type_code)
    if not endpoint:
        return jsonify({"error": f"Invalid number type: {type_code}"}), 400

    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }

        response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers)
        response.raise_for_status()
        numbers = response.json().get("numbers", [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    window_prev_state = window_state.copy()

    window_state = window_state + numbers
    if len(window_state) > WINDOW_SIZE:
        window_state = window_state[-WINDOW_SIZE:]

    avg = statistics.mean(window_state) if window_state else 0

    return jsonify({
        "windowPrevState": window_prev_state,
        "windowCurrState": window_state,
        "numbers": numbers,
        "avg": round(avg, 2)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876, debug=True)
