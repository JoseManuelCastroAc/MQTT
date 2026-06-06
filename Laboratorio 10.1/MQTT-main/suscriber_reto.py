import json
import time
import paho.mqtt.client as mqtt
from pydantic import BaseModel, Field, ValidationError

# 2. Error en la validación de pydantic
class LecturaSensor(BaseModel):
    sensor_id: int
    timestamp: float
    valor: float = Field(..., ge=-50.0, le=100.0) # Validación de límites físicos de temperatura
    unidad: str

BROKER = "broker.hivemq.com"
PUERTO = 1883
# Modificado para tener presente la telemetría usando el comodín de un nivel '+'
TOPICO_COMODIN = "unmsm/callao/camara/+/telemetria"

# Callback cuando el cliente recibe una confirmación de conexión (CONNACK) del broker
def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Conectado exitosamente al Broker MQTT")
        # Suscribirse al tópico de interés
        # Cambiado a la escucha del tópico con comodín para capturar todas las cámaras
        client.subscribe(TOPICO_COMODIN)
        print(f"Suscrito a: {TOPICO_COMODIN}")
    else:
        print(f"Error de conexión. Código de retorno: {rc}")

# Callback cuando llega un mensaje publicado al tópico suscrito
def on_message(client, userdata, msg):
    raw_payload = msg.payload.decode()
    print(f"\n[SUBSCRIBER] Mensaje recibido en {msg.topic}")
    
    # Secciona la ruta del tópico recibido para asi encontrar y traer la sección del ID de la cámara
    partes_topico = msg.topic.split('/')
    id_camara_topico = partes_topico[3] if len(partes_topico) >= 4 else "Desconocida"
    
    try:
        # Intentar transformar de JSON plano a Objeto Validado
        datos_json = json.loads(raw_payload)
        lectura = LecturaSensor(**datos_json)
        
        # Procesar lectura validada de forma segura
        print(f"-> Datos Validados Correctamente. ID: {lectura.sensor_id}")
        print(f"-> Temperatura Registrada: {lectura.valor} {lectura.unidad}")
        
        # 1. Se rompió la cadena de frio, supero el limite de 5°C
        # Evalúa si el valor validado numéricamente es mayor a 5.0 y si sí lo es lanza una alerta
        if lectura.valor > 5.0:
            print(f"[PELIGRO] ¡Se encontro una pérdida de cadena de frío en la cámara {id_camara_topico}! Valor actual: {lectura.valor}°C")
            
    except (json.JSONDecodeError, ValidationError) as error_validacion:
        # Encuentra las fallas de datos que mostraron Pydantic o JSON e imprime
        print("[ALERTA DE SEGURIDAD] Datos corrompidos detectados. Registrando en log...")
        
        # Coloca los errores en el archivo log_errores.txt
        with open("log_errores.txt", "a", encoding="utf-8") as archivo_log:
            fecha_hora = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            archivo_log.write(f"-- ERROR DETECTADO ({fecha_hora}) --\n")
            archivo_log.write(f"Tópico afectado: {msg.topic}\n")
            archivo_log.write(f"Payload corrupto: {raw_payload}\n")
            archivo_log.write(f"Detalle del Error:\n{str(error_validacion)}\n\n")

def main():
    cliente = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    
    # Asignar los callbacks de eventos de red
    cliente.on_connect = on_connect
    cliente.on_message = on_message
    
    cliente.connect(BROKER, PUERTO, 60)
    
    # Iniciar bucle síncrono infinito para escuchar mensajes de red
    cliente.loop_forever()

if __name__ == "__main__":
    main()