import fastapi
from kafka import KafkaConsumer
import json
from datetime import datetime
import threading

app = fastapi.FastAPI()

# Kafka Configuration
KAFKA_URL = "localhost:9092"
TOPIC_PARKING = "parking-spaces"

# Store for reservation events
reservations = []

# Initialize Kafka consumer
parking_consumer = KafkaConsumer(
    TOPIC_PARKING,
    bootstrap_servers=KAFKA_URL
)

def consume_messages():
    for message in parking_consumer:
        try:
            data = json.loads(message.value.decode('utf-8'))
            if data.get("type") == "reservation":
                # Store only the necessary fields
                timestamp = datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
                reservation = {
                    "timestamp": timestamp.strftime("%d/%m/%Y"),  # Format: DD/MM/YYYY
                    "spot_id": data.get("spot_id"),
                    "user_id": data.get("user_id")
                }
                reservations.append(reservation)
        except Exception as e:
            print(f"Error processing message: {e}")

@app.get("/history")
def get_history():
    """Get all reservations sorted by timestamp"""
    return sorted(reservations, key=lambda x: x["timestamp"], reverse=True)

# Start the Kafka consumer thread
consumer_thread = threading.Thread(target=consume_messages, daemon=True)
consumer_thread.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5004) 