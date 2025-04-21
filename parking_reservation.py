import fastapi
from fastapi import HTTPException
from kafka import KafkaProducer
import json
from datetime import datetime
import requests

app = fastapi.FastAPI()

# Kafka Configuration
KAFKA_URL = "localhost:9092"
TOPIC = "parking-spaces"
TOPIC_NOTIFICATIONS = "notifications"

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_URL]
)

reservations = {}

@app.post("/reservations")
def create_reservation(user_id: str, spot_id: str):
    # First check if the spot exists and is available
    try:
        response = requests.get(f"http://localhost:5000/parking-spots")
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to check parking spot status")
        
        spots = response.json()
        spot_exists = False
        spot_available = False
        
        for spot in spots:
            if spot["id"] == spot_id:
                spot_exists = True
                if spot["status"] == "available":
                    spot_available = True
                break
        
        if not spot_exists:
            raise HTTPException(status_code=404, detail="Parking spot not found")
        if not spot_available:
            raise HTTPException(status_code=400, detail="Parking spot is not available")
            
        # Update the parking spot status
        update_response = requests.post(
            f"http://localhost:5000/parking-spots/{spot_id}/update",
            params={"status": "reserved", "user_id": user_id}
        )
        
        if update_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to update parking spot status")
        
        reservation_id = f"RES{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        reservation = {
            "type": "reservation",
            "reservation_id": reservation_id,
            "user_id": user_id,
            "spot_id": spot_id,
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }
        
        reservations[reservation_id] = reservation
        
        producer.send(TOPIC, json.dumps(reservation).encode())
        
        notification = {
            "type": "reservation",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "message": f"Reservation {reservation_id} created for spot {spot_id}"
        }
        producer.send(TOPIC_NOTIFICATIONS, json.dumps(notification).encode())
        
        return {"message": "Reservation created successfully", "reservation": reservation}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to communicate with parking service: {str(e)}")

@app.get("/reservations/{reservation_id}")
def get_reservation(reservation_id: str):
    if reservation_id not in reservations:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservations[reservation_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001) 