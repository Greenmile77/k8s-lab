import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'db-service'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'myappdb'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres123')
    )

@app.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': 'Application is running',
        'service': 'Portfolio Report Generator'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/ready')
def ready():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'ready'})
    except Exception as e:
        return jsonify({'status': 'not ready', 'error': str(e)}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
