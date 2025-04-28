from fastapi import FastAPI, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from kafka import KafkaProducer
import json
from datetime import datetime

app = FastAPI()

KAFKA_URL = "localhost:9092"
TOPIC = "parking-payments"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_URL]
)

class PaymentRequest(BaseModel):
    full_name: str
    amount: float
    payment_type: str

@app.post("/payments")
def process_payment(request: PaymentRequest):
    payment = {
        "type": request.payment_type,
        "timestamp": datetime.now().isoformat(),
        "full_name": request.full_name,
        "amount": request.amount
    }
    
    producer.send(TOPIC, json.dumps(payment).encode())
    
    return {"message": "Payment processed successfully", "payment": payment}

@app.get("/payments/{full_name}")
def get_user_payments(full_name: str):
    return {"message": f"Payment history for user {full_name}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5003) 