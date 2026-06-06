import paho.mqtt.client as mqtt
import json
import time
import random

# Este es el broker público para pruebas propuesto en el laboratorio
BROKER = "broker.hivemq.com" 
PORT = 1883
TOPIC = "fisi/smat/estaciones/1"

client = mqtt.Client()
client.connect(BROKER, PORT)

while True:
    payload = {
        "valor": round(random.uniform(20.0, 60.0), 2),
        "timestamp": time.time()
    }
    # Publicar datos en el "Topic"
    client.publish(TOPIC, json.dumps(payload))
    print(f"Enviado por MQTT: {payload}")
    time.sleep(10)