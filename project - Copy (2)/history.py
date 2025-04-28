import fastapi
from kafka import KafkaConsumer
import json
from datetime import datetime
import threading

app = fastapi.FastAPI()


KAFKA_URL = "localhost:9092"
TOPIC = "notifications"




reservations = []

def consume_messages():    
    
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_URL
    )
    
    for message in consumer:

        consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_URL
    )
        try:
            data = json.loads(message.value.decode('utf-8'))
            if data.get("type") == "reservation":

                reservation = {
                    "timestamp": data.get("timestamp"),
                    "spot_id": data.get("spot_id"),
                    "full_name": data.get("full_name"),
                    "reservation_id": data.get("reservation_id"),
                    "payment_type": data.get("payment_type"),
                    "start_time": data.get("start_time"),
                    "end_time": data.get("end_time"),
                }
                reservations.append(reservation)
        except Exception as e:
            print(f"Error processing message: {e}")


consumer_thread = threading.Thread(target=consume_messages, daemon=True)
consumer_thread.start()

@app.get("/history")
def get_history():
    return sorted(reservations, key=lambda x: x["timestamp"], reverse=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5004) 