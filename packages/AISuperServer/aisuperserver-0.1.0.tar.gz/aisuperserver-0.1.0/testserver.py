from AISuperServer import create_inference_server as InferenceServer

app = InferenceServer(
    model='deepseek-r1',
    stream=True,
    port=8080,
    enable_memory_monitor=True
)

# El servidor ya está corriendo en un thread separado
print("Servidor ejecutándose en http://localhost:8080")
print("Prueba con: curl -X POST http://localhost:8080/api/inference -H 'Content-Type: application/json' -d '{\"query\": \"Hola mundo\"}'")

# El código puede continuar haciendo otras cosas...
import time
while True:
    time.sleep(10)
    print("El servidor sigue ejecutándose...")