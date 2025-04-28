import fastapi
from fastapi import HTTPException
from kafka import KafkaProducer
import json
from datetime import datetime
import requests
from pydantic import BaseModel

app = fastapi.FastAPI()

KAFKA_URL = "localhost:9092"
TOPIC = "parking-spaces"
TOPIC_NOTIFICATIONS = "notifications"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_URL]
)

class ReservationRequest(BaseModel):
    full_name: str
    spot_id: str
    payment_type: str
    start_time: str
    end_time: str

@app.post("/reservations")
def create_reservation(request: ReservationRequest):
    full_name = request.full_name
    spot_id = request.spot_id
    payment_type = request.payment_type
    start_time = request.start_time
    end_time = request.end_time

    try:
        response = requests.get("http://localhost:5000/parking-spots")
        if response.status_code == 200:
            spots = response.json()
            for spot in spots:
                if spot.get("full_name") == full_name and spot["status"] == "reserved":
                    raise HTTPException(status_code=400, detail="You already have an active reservation")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Could not check user reservations")
            

    try:
        response = requests.get(f"http://localhost:5005/availability/{spot_id}")
        if response.status_code == 200:
            availability = response.json()
            if not availability["is_available"]:
                raise HTTPException(status_code=400, detail="Parking spot is not available")
        else:
            raise HTTPException(status_code=400, detail="Failed to check spot availability")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Could not connect to availability service")
            
    payment_response = requests.post(
        "http://localhost:5003/payments",
        json={
            "full_name": full_name,
            "amount": 10.00,
            "payment_type": payment_type
        }
    )
    
    update_response = requests.post(
        f"http://localhost:5000/parking-spots/{spot_id}/update",
        params={"status": "Occupied", "full_name": full_name}
    )
    
    if update_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to update parking spot status")
    
    reservation_id = f"RES{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    reservation = {
        "type": "reservation",
        "reservation_id": reservation_id,
        "full_name": full_name,
        "spot_id": spot_id,
        "status": "confirmed",
        "timestamp": datetime.now().isoformat(),
        "payment_type": payment_type,
        "start_time": start_time,
        "end_time": end_time
    }
    
    producer.send(TOPIC, json.dumps(reservation).encode())
    
    notification = {
        "type": "reservation",
        "timestamp": datetime.now().isoformat(),
        "full_name": full_name,
        "spot_id": spot_id,
        "reservation_id": reservation_id,
        "payment_type": payment_type,
        "start_time": start_time,
        "end_time": end_time,
        "message": f"Reservation {reservation_id} created for spot {spot_id}"
    }
    producer.send(TOPIC_NOTIFICATIONS, json.dumps(notification).encode())
    
    return {"message": "Reservation created successfully", "reservation": reservation}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001) 