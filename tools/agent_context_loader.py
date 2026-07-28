# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
# tools/agent_context_loader.py

import os

def load_master_prompt():
    """
    Carga el contenido del prompt maestro y lo devuelve como una cadena.

    Esta función es la única fuente de verdad para el contexto inicial
    de cualquier agente de IA que opere en el repositorio de Sentinel.
    """
    try:
        # La ruta es relativa a la raíz del proyecto, asumiendo que el script
        # se ejecuta desde la raíz o que la ruta es accesible.
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'SENTINEL_AGENT_MASTER_PROMPT.md'
        )
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    except FileNotFoundError:
        error_message = (
            "CRITICAL ERROR: 'SENTINEL_AGENT_MASTER_PROMPT.md' not found.
"
            "The agent cannot be initialized without its master prompt.
"
            "Ensure you are running this script from within the Sentinel project directory."
        )
        print(error_message)
        return None

def main():
    """
    Función principal para ejecutar el cargador de contexto desde la línea de comandos.
    Imprime el prompt maestro a la salida estándar.
    """
    master_prompt = load_master_prompt()
    if master_prompt:
        print(master_prompt)

if __name__ == "__main__":
    main()
