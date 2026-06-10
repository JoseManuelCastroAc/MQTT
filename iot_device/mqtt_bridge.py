import time
import json
import sys
import requests
import paho.mqtt.client as mqtt

# =============================================
# CONFIGURACIÓN DEL ENTORNO SMAT
# =============================================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883
MQTT_TOPIC  = "fisi/smat/estaciones/+/lecturas"  # Wildcard dinámico para estaciones
API_URL     = "http://localhost:8000/lecturas/"

# Token de seguridad de la API (Usuario validado: admin_fisi)
JWT_TOKEN   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl9maXNpIiwiZXhwIjoxNzg0ODg5NjAwfQ..." 

# =============================================
# FILTRO DEADBAND — Registro de Memoria Local
# =============================================
UMBRAL_CAMBIO_PORCENTAJE = 5.0   # Mínimo de variación requerido
TIEMPO_MINIMO_REPORTE    = 60    # Segundos máximos de tolerancia sin cambios

# Estructura de caché modificada para el análisis de redundancia
registro_cache = {}


def validar_filtro_ruido(estacion_id: int, nuevo_valor: float) -> tuple:
    """
    Evalúa si la lectura entrante pasa el filtro de optimización de red o se bloquea.
    """
    ahora = time.time()

    # Si es la primera lectura de la estación, se le da paso libre
    if estacion_id not in registro_cache:
        return True, "Inicialización de la estación en el bridge"

    datos_anteriores = registro_cache[estacion_id]
    valor_previo     = datos_anteriores["valor"]
    tiempo_previo    = datos_anteriores["timestamp"]

    # Condición 1 — Verificación del reporte mínimo de vida (Heartbeat)
    segundos_transcurridos = ahora - tiempo_previo
    if segundos_transcurridos > TIEMPO_MINIMO_REPORTE:
        return True, f"Heartbeat validado ({int(segundos_transcurridos)}s de inactividad)"

    # Condición 2 — Variación porcentual matemática
    if valor_previo != 0:
        variacion = abs((nuevo_valor - valor_previo) / valor_previo) * 100
    else:
        variacion = 100.0

    if variacion > UMBRAL_CAMBIO_PORCENTAJE:
        return True, f"Cambio de magnitud crítico ({variacion:.2f}% > {UMBRAL_CAMBIO_PORCENTAJE}%)"

    # Si no cumple ninguna, es un dato redundante (ruido)
    return False, f"Ruido filtrado (Variación insignificante de {variacion:.2f}%)"


# =============================================
# CALLBACKS ASÍNCRONOS MQTT
# =============================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("🟢 Conectado exitosamente al Broker MQTT")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Escuchando transmisiones en el tópico: {MQTT_TOPIC}\n")
    else:
        print(f"🔴 Error de conexión al Broker. Código: {rc}")
        sys.exit(1)


def on_message(client, userdata, msg):
    try:
        # 1. Extracción y decodificación del paquete binario
        payload_raw = msg.payload.decode("utf-8")
        data_json   = json.loads(payload_raw)

        # 2. Parseo dinámico de la ruta del tópico para extraer el identificador
        topic_parts = msg.topic.split('/')
        estacion_id = int(topic_parts[3])
        nuevo_valor = float(data_json["valor"])

        print(f"\n📩 Telemetría recibida — Estación [{estacion_id}]: {nuevo_valor} cm")

        # 3. Aplicación del Filtro de Ruido (Reto Técnico)
        enviar_a_db, justificacion = validar_filtro_ruido(estacion_id, nuevo_valor)

        if not enviar_a_db:
            print(f"🚫 [FILTRADO] Dato bloqueado — {justificacion}")
            return

        # 4. Formatear cuerpo compatible con el Pydantic Schema de FastAPI
        api_payload = {
            "valor":       nuevo_valor,
            "estacion_id": estacion_id
        }

        # 5. Inyección síncrona HTTP POST mediante cabecera Bearer Token
        headers = {
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {JWT_TOKEN}"
        }
        response = requests.post(API_URL, json=api_payload, headers=headers, timeout=5)

        if response.status_code in (200, 201):
            # 6. Guardar en memoria caché únicamente tras una persistencia exitosa
            registro_cache[estacion_id] = {
                "valor":     nuevo_valor,
                "timestamp": time.time()
            }
            print(f"💾 [DB Sincronizada] {nuevo_valor} cm guardado — {justificacion}")
        else:
            print(f"⚠️  [Fallo de Ingesta] API rechazó el dato. Código HTTP: {response.status_code}")

    except KeyError as e:
        print(f"❌ Error de esquema: Falta la llave {e} en el payload MQTT.")
    except ValueError:
        print("❌ Error de casteo: El valor o ID de estación no son numéricos.")
    except Exception as e:
        print(f"❌ Error crítico en el Bridge: {e}")


# =============================================
# INICIO DEL DAEMON PUENTE
# =============================================
print("=" * 55)
print("  🚀 Inicializando el Bridge de Acoplamiento SMAT...")
print("=" * 55)

bridge_client = mqtt.Client()
bridge_client.on_connect = on_connect
bridge_client.on_message = on_message

try:
    bridge_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    bridge_client.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 Bridge detenido por el administrador.")