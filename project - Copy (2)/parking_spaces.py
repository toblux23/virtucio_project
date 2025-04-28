import fastapi
from fastapi import HTTPException
from kafka import KafkaProducer
import json
from datetime import datetime

app = fastapi.FastAPI()


KAFKA_URL = "localhost:9092"
TOPIC = "parking-spaces"


producer = KafkaProducer(
    bootstrap_servers=[KAFKA_URL]
)

parking_spots = {
    "P1": {"status": "available", "full_name": None},
    "P2": {"status": "available", "full_name": None},
    "P3": {"status": "available", "full_name": None},
    "P4": {"status": "available", "full_name": None},
    "P5": {"status": "available", "full_name": None},
    "P6": {"status": "available", "full_name": None},
    "P7": {"status": "available", "full_name": None},
    "P8": {"status": "available", "full_name": None},
    "P9": {"status": "available", "full_name": None},
    "P10": {"status": "available", "full_name": None},
    "P11": {"status": "available", "full_name": None},
    "P12": {"status": "available", "full_name": None},
    "P13": {"status": "available", "full_name": None},
    "P14": {"status": "available", "full_name": None},
    "P15": {"status": "available", "full_name": None},
    "P16": {"status": "available", "full_name": None},
    "P17": {"status": "available", "full_name": None},
    "P18": {"status": "available", "full_name": None},
    "P19": {"status": "available", "full_name": None},
    "P20": {"status": "available", "full_name": None}
}

@app.get("/parking-spots")
def get_parking_spots():
    return [{"id": id, **spot} for id, spot in parking_spots.items()]

@app.post("/parking-spots/{spot_id}/update")
def update_spot(spot_id: str, status: str, full_name: str = None):
    if spot_id not in parking_spots:
        raise HTTPException(status_code=404, detail="Spot not found")
    
    parking_spots[spot_id]["status"] = status
    parking_spots[spot_id]["full_name"] = full_name
    
    message = {
        "type": "spot_update",
        "timestamp": datetime.now().isoformat(),
        "spot_id": spot_id,
        "status": status,
        "full_name": full_name
    }
    producer.send(TOPIC, json.dumps(message).encode())
    
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000) 