
import sys
import os
from google import genai
from google.genai import types

def test_gemini():
    print("🤖 Iniciando prueba de Google GenAI SDK (v1.60.0)...")

    # Intentamos detectar el Project ID de las variables de entorno comunes
    # Si no existen, el cliente intentará usar ADC (Application Default Credentials)
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    try:
        if project_id:
            print(f"📍 Configurando cliente para Vertex AI (Proyecto: {project_id}, Región: {location})")
            client = genai.Client(vertexai=True, project=project_id, location=location)
        else:
            print("⚠️ No se detectó GOOGLE_CLOUD_PROJECT explícito.")
            print("🔄 Intentando inicialización automática (buscando credenciales por defecto)...")
            # Si tienes configurado 'gcloud auth application-default login', esto funcionará automáticamente
            client = genai.Client(vertexai=True, location=location)

        # Nombre del modelo: 'gemini-1.5-flash-002' es rápido y eficiente para pruebas
        model_name = "gemini-1.5-flash-002"
        
        print(f"⚡ Enviando prompt a {model_name}...")
        
        response = client.models.generate_content(
            model=model_name,
            contents="Explica brevemente qué es la computación cuántica en una sola frase."
        )

        print("\n✅ RESPUESTA RECIBIDA:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        
    except Exception as e:
        print("\n❌ ERROR:")
        print(f"No se pudo conectar con Gemini. Detalles: {e}")
        print("\n💡 SUGERENCIA:")
        print("Si es un error de autenticación, asegúrate de haber ejecutado:")
        print("  gcloud auth application-default login")
        print("O configura la variable GOOGLE_CLOUD_PROJECT en tu entorno.")

if __name__ == "__main__":
    test_gemini()
