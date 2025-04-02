from flask import Flask, jsonify
import requests
import statistics

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

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQzNjAxNTYxLCJpYXQiOjE3NDM2MDEyNjEsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjM1MDliMjRlLWI3N2UtNDEzYi1iODJkLWYxMTcxNTA4ZmFjOSIsInN1YiI6IjIyMDUxNDUxQGtpaXQuYWMuaW4ifSwiZW1haWwiOiIyMjA1MTQ1MUBraWl0LmFjLmluIiwibmFtZSI6InNhaGlsIGt1bWFyIGNob3VkaGFyeSIsInJvbGxObyI6IjIyMDUxNDUxIiwiYWNjZXNzQ29kZSI6Im53cHdyWiIsImNsaWVudElEIjoiMzUwOWIyNGUtYjc3ZS00MTNiLWI4MmQtZjExNzE1MDhmYWM5IiwiY2xpZW50U2VjcmV0IjoiTm5US21Cem1nY3pKYWdTRSJ9.trI8q2wwiQF_zcqmYG2vWM9c9C4B1k_ya5uWxDbheVk"


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
