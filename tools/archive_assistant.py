# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
import os
import re
import sys
from datetime import datetime

def archive_assistant(directory):
    date_str = datetime.now().strftime('%Y-%m-%d')
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}_')
    
    if not os.path.exists(directory):
        print(f'Error: El directorio {directory} no existe.')
        return

    print(f'\n--- Asistente de Archivistas Sentinel (Fecha hoy: {date_str}) ---')
    print(f'Escaneando: {directory}\n')

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    if not files:
        print('No se encontraron archivos en este directorio.')
        return

    for filename in files:
        if not date_pattern.match(filename):
            new_name = f'{date_str}_{filename}'
            # Pregunta al usuario para que mantengas el control total
            print(f'  [?] ¿Rotular? {filename}  -->  {new_name}')
            choice = input('      (s/n/skip): ').lower()
            
            if choice == 's':
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_name)
                os.rename(old_path, new_path)
                print(f'      ✅ Renombrado.')
            else:
                print(f'      ⏭️ Omitido.')
        else:
            print(f'  [OK] Ya rotulado: {filename}')

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    archive_assistant(target)
