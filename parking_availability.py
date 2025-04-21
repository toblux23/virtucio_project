from kafka import KafkaConsumer, KafkaProducer
import json
from datetime import datetime

# Kafka Configuration
KAFKA_URL = "localhost:9092"
TOPIC = "parking-spaces"
TOPIC_AVAILABILITY = "parking-availability"

# Initialize Kafka producer and consumer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_URL]
)

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_URL
)

def main():
    try:
        for message in consumer:
            try:
                # Manually decode the message value
                data = json.loads(message.value.decode('utf-8'))
                
                # Create availability update message
                availability = {
                    "timestamp": datetime.now().isoformat(),
                    "spot_id": data.get("spot_id"),
                    "status": data.get("status"),
                    "user_id": data.get("user_id")
                }
                
                # Manually encode and send the message
                producer.send(
                    TOPIC_AVAILABILITY,
                    value=json.dumps(availability).encode('utf-8')
                )
                
                print(f"Processed parking spot update: {json.dumps(availability, indent=2)}")
                
            except Exception as e:
                print(f"Error processing message: {e}")
                
    except KeyboardInterrupt:
        print("\nShutting down Parking Availability Service...")
    finally:
        consumer.close()
        producer.close()

main() 