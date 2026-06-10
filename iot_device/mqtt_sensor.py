import requests
import time
import random

# =============================================
# CONFIGURACIÓN DEL CLIENTE HTTP
# =============================================
API_URL     = "http://localhost:8000/lecturas/"
ESTACION_ID = 1          
TOKEN_JWT   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl9maXNpIiwiZXhwIjoxNzg0ODg5NjAwfQ..." 

# Parámetros operativos del desborde
UMBRAL_ALERTA        = 70.0
INTERVALO_NORMAL     = 10  
INTERVALO_EMERGENCIA = 2   


# =============================================
# EMULACIÓN DE ENTRADAS DE RESTRICCIÓN
# =============================================
def leer_sensor_emulado() -> float:
    """ Simula la recolección física del nivel de agua (0-100 cm) """
    return round(random.uniform(10.5, 85.0), 2)


# =============================================
# PROCESAMIENTO CONTINUO DE PETICIONES REST
# =============================================
def enviar_telemetria():
    print(f"{'='*55}")
    print(f"  Iniciando Emisor IoT — Estación {ESTACION_ID}")
    print(f"{'='*55}\n")

    while True:
        valor_actual = leer_sensor_emulado()

        # Evaluación adaptativa del intervalo de red según criticidad
        if valor_actual > UMBRAL_ALERTA:
            print(f"[ALERTA] Umbral de inundación superado: {valor_actual} cm")
            delay = INTERVALO_EMERGENCIA
            modo_operativo = "EMERGENCIA"
        else:
            delay = INTERVALO_NORMAL
            modo_operativo = "Normal"

        # Construcción de la carga útil HTTP
        payload = {
            "valor":       valor_actual,
            "estacion_id": ESTACION_ID
        }
        headers = {
            "Authorization": f"Bearer {TOKEN_JWT}"
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=5)

            if response.status_code in (200, 201):
                print(f"[OK]    Lectura enviada: {valor_actual} cm  | Modo: {modo_operativo} | Próxima en {delay}s")
            else:
                print(f"[ERROR] Código HTTP: {response.status_code} — {response.text}")

        except requests.exceptions.ConnectionError:
            print(f"[CRÍTICO] Servidor inaccesible. Reintentando en {delay}s...")
        except Exception as e:
            print(f"[CRÍTICO] Error inesperado detectado: {e}")

        time.sleep(delay)


if __name__ == "__main__":
    enviar_telemetria()