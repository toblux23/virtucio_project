from kafka import KafkaConsumer
import json
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

# In-memory status store
parking_status = {}

# Kafka Configuration
KAFKA_URL = "localhost:9092"
TOPIC = "parking-spaces"

# Initialize Kafka consumer
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_URL
)

def update_status():
    """Update the status of a parking spot"""
    for message in consumer:
        data = json.loads(message.value.decode('utf-8'))
        spot_id = data.get("spot_id")
        if spot_id:
            parking_status[spot_id] = {
                "status": data.get("status"),
                "user_id": data.get("user_id")
            }

@app.route('/status')
def get_status():
    """Get current status of all parking spots"""
    return jsonify(parking_status)

@app.route('/status/<spot_id>', methods=['GET'])
def get_spot_status(spot_id):
    """Get status of a specific parking spot"""
    return jsonify(parking_status.get(spot_id, {}))

def consume_messages():
    """Consume messages from Kafka and update status"""
    try:
        for message in consumer:
            try:
                data = json.loads(message.value.decode('utf-8'))
                update_status()
                print(f"Updated status for spot {data.get('spot_id')}")
            except Exception as e:
                print(f"Error processing message: {e}")
    except KeyboardInterrupt:
        print("\nShutting down Parking Status Service...")
    finally:
        consumer.close()

if __name__ == "__main__":
    # Start Flask app in a separate thread
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(port=5005))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start consuming messages
    consume_messages() 