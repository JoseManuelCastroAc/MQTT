import paho.mqtt.client as mqtt
import json
import time
import random

# =============================================
# CONFIGURACIÓN DEL EMISOR
# =============================================
BROKER      = "broker.hivemq.com"
PORT        = 1883
ESTACION_ID = 1
TOPIC       = f"fisi/smat/estaciones/{ESTACION_ID}/lecturas"

# =============================================
# CICLO PRINCIPAL DE TRANSMISIÓN
# =============================================
def enviar_datos_mqtt():
    client = mqtt.Client()
    client.connect(BROKER, PORT)

    print(f"{'='*55}")
    print(f"  Sensor MQTT iniciado — Publicando en: {TOPIC}")
    print(f"{'='*55}\n")

    while True:
        # Generación de la lectura de telemetría simulada
        valor_medido = round(random.uniform(20.0, 85.0), 2)

        payload_datos = {
            "valor":     valor_medido,
            "timestamp": time.time()
        }

        client.publish(TOPIC, json.dumps(payload_datos))

        # Alarma visual integrada en la consola para picos críticos
        if valor_medido > 70.0:
            print(f"🚨 [ALERTA MQTT] Valor crítico publicado: {valor_medido} cm")
        else:
            print(f"📡 [MQTT] Publicado: {valor_medido} cm → Topic: {TOPIC}")

        time.sleep(10)

if __name__ == "__main__":
    enviar_datos_mqtt()