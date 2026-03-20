#!/usr/bin/env python3
import sys
import os
import asyncio

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    from google.api_core import exceptions as google_exceptions
except ImportError:
    print("❌ ERROR: La librería 'google-cloud-aiplatform' no está instalada.")
    print("   Por favor, ejecute: pip install google-cloud-aiplatform")
    sys.exit(1)

async def test_gemini():
    print("🤖 Iniciando prueba de conexión con Google Vertex AI SDK...")
    print("-" * 50)

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    try:
        if not project_id:
            print("❌ ERROR: GOOGLE_CLOUD_PROJECT no está configurado.")
            sys.exit(1)

        print(f"📍 Configurando para Vertex AI (Proyecto: {project_id}, Región: {location})")
        vertexai.init(project=project_id, location=location)

        model_name = os.getenv("GOOGLE_MODEL", "gemini-2.5-pro")
        model = GenerativeModel(model_name)

        print(f"✅ Cliente configurado. Modelo: {model_name}")
        print("⚡ Enviando prompt de prueba...")

        prompt = "Eres un experto en seguridad de sistemas. Dame 3 consejos clave para proteger un servidor Linux en producción."
        response = await model.generate_content_async(prompt)

        print("\n" + "="*15 + " RESPUESTA DE GEMINI " + "="*15)
        print(response.text.strip())
        print("=" * 50)
        print("\n✅ Prueba completada exitosamente.")

    except google_exceptions.NotFound as e:
        print("\n❌ ERROR: Modelo no encontrado (404 Not Found).")
        print(f"   El modelo '{model_name}' no existe o no está disponible en la región '{location}'.")
        print("\n💡 POSIBLES SOLUCIONES:")
        print("   1. Confirma que el nombre del modelo es exacto.")
        print("   2. Verifica que el proyecto y la región sean correctos.")
        print("   3. Asegúrate que el proyecto esté en la allowlist si el modelo es privado.")
    except google_exceptions.PermissionDenied as e:
        print("\n❌ ERROR: Permiso denegado (403 Forbidden).")
        print(f"   Detalles: {e}")
        print("\n💡 POSIBLES SOLUCIONES:")
        print("   1. Asegúrate de que la API de Vertex AI ('vertexai.googleapis.com') esté habilitada.")
        print("   2. Verifica que la cuenta de servicio o tus credenciales (ADC) tengan el rol 'Vertex AI User'.")
    except Exception as e:
        print("\n❌ ERROR INESPERADO DURANTE LA PRUEBA:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Detalles: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
