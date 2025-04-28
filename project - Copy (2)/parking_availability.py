import fastapi
from kafka import KafkaConsumer, KafkaProducer
import json
from datetime import datetime
import threading
import requests

app = fastapi.FastAPI()

KAFKA_URL = "localhost:9092"
TOPIC_SPACES = "parking-spaces"
TOPIC_AVAILABILITY = "parking-availability"

parking_spots = {}

# Initialize spots from parking_spaces service
def init_parking_spots():
    try:
        response = requests.get("http://localhost:5000/parking-spots")
        if response.status_code == 200:
            spots = response.json()
            for spot in spots:
                parking_spots[spot["id"]] = {
                    "status": spot["status"],
                    "full_name": spot.get("full_name"),
                    "last_updated": datetime.now().isoformat()
                }
            print(f"Initialized parking spots: {parking_spots}")
    except Exception as e:
        print(f"Error initializing parking spots: {e}")

# Initialize parking spots before starting the service
init_parking_spots()

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_URL]
)

consumer = KafkaConsumer(
    TOPIC_SPACES,
    bootstrap_servers=KAFKA_URL,
    auto_offset_reset='latest',
    consumer_timeout_ms=1000
)

def consume_messages():
    print("Starting to consume messages...")
    for message in consumer:
        try:
            data = json.loads(message.value.decode('utf-8'))
            print(f"Received message: {data}")
            spot_id = data.get("spot_id")
            status = data.get("status")
            full_name = data.get("full_name")
            
            if spot_id:
                parking_spots[spot_id] = {
                    "status": status,
                    "full_name": full_name,
                    "last_updated": datetime.now().isoformat()
                }
                print(f"Updated spot {spot_id} status to {status}, current spots: {parking_spots}")
        except Exception as e:
            print(f"Error processing message: {e}")

consumer_thread = threading.Thread(target=consume_messages)
consumer_thread.daemon = True
consumer_thread.start()

@app.get("/availability/{spot_id}")
def check_availability(spot_id: str):
    print(f"Checking availability for spot {spot_id}, current spots: {parking_spots}")
    if spot_id in parking_spots:
        spot = parking_spots[spot_id]
        result = {
            "spot_id": spot_id,
            "is_available": spot["status"] == "available",
            "status": spot["status"],
            "full_name": spot.get("full_name"),
            "last_updated": spot["last_updated"]
        }
        print(f"Returning availability: {result}")
        return result
    print(f"Spot {spot_id} not found in parking_spots")
    return {
        "spot_id": spot_id,
        "is_available": False,
        "status": "unknown",
        "full_name": None,
        "last_updated": datetime.now().isoformat()
    }

@app.get("/availability")
def get_all_availability():
    available_spots = {}
    for spot_id, spot in parking_spots.items():
        available_spots[spot_id] = {
            "spot_id": spot_id,
            "is_available": spot["status"] == "available",
            "status": spot["status"],
            "full_name": spot.get("full_name"),
            "last_updated": spot["last_updated"]
        }
    return available_spots

if __name__ == "__main__":
    print("Parking Availability Service starting...")
    consumer_thread = threading.Thread(target=consume_messages, daemon=True)
    consumer_thread.start()
    print("Parking Availability Service started...")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5005)
