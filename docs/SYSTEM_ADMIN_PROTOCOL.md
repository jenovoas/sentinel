# 📡 Sentinel System Administration Protocol (SSAP) v1.0

Este documento define el **Contrato de Operación** entre el Operador Humano (DevOps) y la Inteligencia Artificial (SemSH).

## 1. Principios Fundamentales
1.  **La IA propone, el Humano dispone**: SemSH nunca ejecuta cambios de estado (escritura/reinicio) sin confirmación explícita o Playbook pre-autorizado.
2.  **Whitelist Operativa**: Solo se permiten comandos envueltos (`sctl`, `sdocker`, `spkg`, `sem`). Comandos crudos (`rm`, `dd`, `iptables`) están prohibidos para la IA.
3.  **Observabilidad Primero**: Antes de cualquier acción, la IA debe consultar el estado (`sctl status --json`, `sdocker status`).

## 2. Comandos Autorizados (Safe Harbor)

| Comando | Función | Riesgo | Validación IA |
| :--- | :--- | :--- | :--- |
| `sctl status` | Ver salud del sistema | Nulo | Automática |
| `sdocker status` | Ver contenedores | Nulo | Automática |
| `sdocker safe-restart` | Reiniciar servicio | Medio | Requiere Whitelist |
| `spkg install` | Instalar paquete SIP | Alto | Requiere Firma + Semántica |
| `sem run <playbook>` | Ejecutar receta YAML | Variable | Según Playbook |

## 3. Playbooks (Recetas Estándar)
La administración se realiza mediante **Playbooks Declarativos** en `/opt/sentinel/playbooks/`.
*   SemSH lee estos archivos para entender *qué* hacer paso a paso.
*   Ejemplo: `sem run backup_db` ejecuta la secuencia definida en `backup_db.yaml`.

## 4. Flujos de Trabajo (Workflows)

### Caso A: "El sistema está lento"
1.  **Observación**: IA ejecuta `sctl status` y detecta `Load Avg > 4.0`.
2.  **Juicio**: IA sugiere "Aplicar perfil Performance".
3.  **Acción**: Humano aprueba -> IA ejecuta `sctl tune --profile performance`.

### Caso B: "Necesito reiniciar la BD"
1.  **Intención**: Humano escribe "Reinicia la base de datos".
2.  **Guardia**: IA verifica dependencias (¿Hay usuarios conectados?).
3.  **Ejecución**: IA ejecuta `sdocker safe-restart postgres`.
