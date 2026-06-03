import time
import random
import json
import paho.mqtt.client as mqtt

# Configuración del Broker Público de Pruebas
BROKER = "broker.hivemq.com"
PUERTO = 1883
TOPICO = "unmsm/fisi/cc/sensor/temperatura"

def conectar_mqtt():
    # Inicializar cliente MQTT utilizando la API moderna v2
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    
    print(f"Conectando al broker {BROKER}...")
    client.connect(BROKER, PUERTO, 60)
    return client

def main():
    cliente = conectar_mqtt()
    cliente.loop_start() # Iniciar el bucle de red de fondo
    
    # // Lista de cámaras para enviar datos intercalados de cada una
    camaras = [101, 102]
    indice_camara = 0
    
    try:
        while True:
            # Selecciona el ID de la cámara actual según la rotación del índice
            id_camara = camaras[indice_camara]
            
            # Etructura el tópico dinámico usando el ID de la cámara correspondiente
            topico_dinamico = f"unmsm/callao/camara/{id_camara}/telemetria"
            
            tipo_envio = random.choices(["OK", "FALLA_TEXTO", "FALLA_LIMITE"], weights=[85, 7, 8])[0]
            
            if tipo_envio == "OK":
                temperatura = round(random.uniform(2.0, 9.0), 2)
            elif tipo_envio == "FALLA_TEXTO":
                temperatura = "ERROR_SENSOR_ALTA_HUMEDAD"
            elif tipo_envio == "FALLA_LIMITE":
                temperatura = 150.0
                
            # Generar datos simulados del sensor
            datos_sensor = {
                "sensor_id": id_camara,
                "timestamp": time.time(),
                "valor": temperatura,
                "unidad": "Celsius"
            }
            
            # Serializar diccionario a JSON string
            mensaje = json.dumps(datos_sensor)
            
            # Publicar el mensaje con QoS 1 (Asegurar entrega)
            # Cambiado al tópico dinámico de la cámara para cumplir con el formato del reto
            info = cliente.publish(topico_dinamico, mensaje, qos=1)
            info.wait_for_publish() # Bloquear hasta asegurar el envío
            
            print(f"[PUBLISHER] Enviado a {topico_dinamico} (Modo: {tipo_envio}): {mensaje}")
            
            # Incrementa el índice para hacer la alternancia entre las cámaras disponibles
            indice_camara = (indice_camara + 1) % len(camaras)
            time.sleep(3) # Esperar 3 segundos
            
    except KeyboardInterrupt:
        print("\nDeteniendo publicador...")
    finally:
        cliente.loop_stop()
        cliente.disconnect()

if __name__ == "__main__":
    main()