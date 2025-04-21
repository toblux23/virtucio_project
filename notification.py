import fastapi
from kafka import KafkaProducer
import json
from datetime import datetime

app = fastapi.FastAPI()

# Kafka Configuration
KAFKA_URL = "localhost:9092"
TOPIC = "notifications"

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_URL]
)

@app.post("/notifications")
def send_notification(user_id: str, message: str, notification_type: str):
    notification = {
        "type": notification_type,
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "message": message
    }
    
    # Send to notifications topic
    producer.send(TOPIC, json.dumps(notification).encode())
    
    return {"message": "Notification sent successfully", "notification": notification}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5002) 