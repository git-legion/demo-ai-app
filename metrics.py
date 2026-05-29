from flask import Flask
from prometheus_client import Counter, generate_latest

app = Flask(__name__)

REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total Application Requests'
)

@app.route('/metrics')
def metrics():

    REQUEST_COUNT.inc()

    return generate_latest(), 200, {
        'Content-Type': 'text/plain'
    }

app.run(host='0.0.0.0', port=5001)

