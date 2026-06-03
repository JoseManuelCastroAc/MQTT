# MQTT
## Pregunta Crítica: ¿Por qué REST (HTTP) no sirve para sensores de alta frecuencia?



Principalmente por 2 razones: 



1. **Agotamiento del Servidor (Hilos de ejecución):** HTTP es un protocolo síncrono Es decir cada petición que envía un sensor obliga al servidor a abrir y mantener un hilo de trabajo dedicado hasta recibir respuesta, lo cual es insostenible al darse una lata frecuencia de estas peticiones

2. **Mucha Basura en la Red (Sobrecarga de bytes):** Como se menciono en clase por el tema de las cabeceras llega a ser sumamente pesado realizar un REST HTTP, que pesa alrededor de 500 bytes, a diferencia de la cabecera de MQTT, que pesa 2bytes

---



## Pregunta Práctica: ¿Cuándo usar QoS 2 en lugar de QoS 0?



El nivel **QoS 2** asegura que el mensaje llegue **exactamente una vez** (ni se pierde, ni se duplica). Es obligatorio usarlo en sistemas donde no se permite una mala administración de los datos, por ejemplo. En un sistema financiero causaría errores logísticos internos tan solo perder o duplicar un dato financiero, lo cual provoca que la empresa necesariamente debe acceder al nivel QoS2



---



## Reflexión Ética / RSU: MQTT y la Sostenibilidad en el Perú Rural



La implemetancion de MQTT aporto de forma muy grande al acceso sostenible de las zonas rurales y vulnerables, brindando:



* **Inclusión ante la Brecha Digital: permite que a pesar de no tener grandes dispositivos tecnologicos, puedan gozar de algunos beneficios que ellos no han podido tener por la misma brecha.** 

* **Ahorro Energético: Menos datos implica menor cantidad de uso de energia lo cual es muy util en el contexto planteado para usar MQTT** 
