# 📋 PATENT FILING - ADDITIONAL BLOCKS
**Sentinel Cortex™ - Resumen de Invención y Reivindicaciones Dependientes**

**Fecha:** 17 Diciembre 2025 - 04:35 AM  
**Propósito:** Bloques adicionales listos para patent attorney  
**Status:** ✅ LEGAL LANGUAGE READY

---

## 📊 BLOQUE 1: RESUMEN DE LA INVENCIÓN (ABSTRACT/SUMMARY)

### Para Sección "Summary of the Invention" del Patent Application:

**Título:** Sistema de Seguridad Autónomo con Arquitectura de Dual-Guardián y Auto-Regeneración

**Resumen (VERSIÓN CONCISA RECOMENDADA):**

En una realización preferente, la invención propone una arquitectura de "doble guardián" para sistemas AIOps en la que un primer guardián residente en el kernel intercepta llamadas al sistema en tiempo real mediante programas eBPF y filtros seccomp, mientras que un segundo guardián en espacio de usuario valida la integridad de las acciones propuestas por la capa de IA y supervisa el correcto funcionamiento del primer guardián. Ambos guardianes comparten un mecanismo de latido atómico que permite detectar, en cuestión de segundos, la detención o compromiso de uno de ellos y disparar de forma automática un protocolo de auto-regeneración del subsistema de seguridad, cargando reglas de denegación estáticas desde almacenamiento protegido y restaurando los ganchos de intercepción correspondientes sin necesidad de intervención humana. Este enfoque reduce de manera sustancial la probabilidad de fallo silencioso del propio mecanismo de defensa y proporciona una capa adicional de resiliencia frente tanto a ataques externos como a degradaciones internas del sistema.

---

### Resumen (Versión Extendida - Alternativa):

La presente invención se refiere a un sistema y método para monitoreo autónomo de seguridad en sistemas de operaciones de inteligencia artificial (AIOps), que comprende una arquitectura de dual-guardián con capacidades de vigilancia mutua y auto-regeneración sin intervención humana.

El sistema comprende un primer componente guardián (Guardian-Alpha) que opera en espacio de kernel y ejecuta intercepción de llamadas del sistema en tiempo real mediante programas eBPF (extended Berkeley Packet Filter), y un segundo componente guardián (Guardian-Beta) que opera en espacio de usuario y verifica la integridad de configuraciones y políticas de seguridad. Ambos guardianes mantienen una referencia compartida a un contador de tiempo atómico de 64 bits que actúa como señal de latido ("heartbeat"), permitiendo la detección bidireccional de fallos en cualquiera de los componentes.

En una realización preferente, el Guardian-Alpha actualiza el contador compartido con una frecuencia de entre 100 y 500 milisegundos durante el procesamiento de eventos de kernel, mientras que el Guardian-Beta verifica dicho contador aproximadamente cada segundo. Si el tiempo transcurrido desde la última actualización excede un umbral configurable (típicamente cinco segundos), el sistema activa automáticamente un protocolo regenerativo que incluye la recarga del programa eBPF, la reinstalación de filtros de seguridad, y la restauración de políticas desde almacenamiento inmutable, todo sin requerir intervención manual.

La arquitectura de vigilancia bidireccional permite que, en caso de fallo del Guardian-Beta, el Guardian-Alpha entre en un modo de operación degradado pero seguro, aplicando un conjunto restrictivo de reglas predefinidas a nivel de kernel. Esta capacidad de auto-diagnóstico y auto-reparación reduce significativamente el tiempo medio de recuperación (MTTR) a menos de siete segundos, comparado con los 5-30 minutos típicos de sistemas que requieren intervención manual.

El sistema es particularmente útil para proteger plataformas AIOps contra ataques de inyección de telemetría (AIOpsDoom), donde logs maliciosos pueden manipular sistemas de inteligencia artificial para ejecutar acciones destructivas. La combinación de intercepción a nivel de kernel, validación multi-factor, y auto-regeneración constituye una mejora no obvia sobre sistemas de monitoreo tradicionales que operan exclusivamente en espacio de usuario o que carecen de mecanismos de auto-reparación.

**Palabras Clave:** AIOps, eBPF, dual-guardian, mutual surveillance, auto-regeneration, kernel-level security, heartbeat mechanism, fail-safe, autonomous monitoring

---

## 📊 BLOQUE 2: REIVINDICACIONES DEPENDIENTES

### Reivindicación Independiente (Claim 3 - Principal):

**Claim 3:** Un sistema de monitoreo autónomo de seguridad que comprende:

(a) Un primer componente guardián (Guardian-Alpha) que opera en espacio de kernel y ejecuta intercepción de llamadas del sistema mediante programas eBPF;

(b) Un segundo componente guardián (Guardian-Beta) que opera en espacio de usuario y verifica integridad de configuraciones de seguridad;

(c) Una referencia compartida a un contador de tiempo atómico de 64 bits accesible por ambos componentes guardianes;

(d) Un mecanismo de vigilancia mutua donde cada componente guardián monitorea el estado operacional del otro mediante verificación periódica de dicho contador de tiempo;

(e) Un protocolo de auto-regeneración que se activa automáticamente cuando el tiempo transcurrido desde la última actualización del contador excede un umbral predeterminado, sin requerir intervención humana.

---

### Reivindicaciones Dependientes:

**Claim 3.A (Dependiente de Claim 3 - VERSIÓN CONCISA RECOMENDADA):** 

El sistema según cualquiera de las reivindicaciones anteriores, en el que el primer guardián y el segundo guardián implementan un mecanismo de vigilancia mutua mediante un contador de tiempo compartido que actúa como señal de latido ("heartbeat"), donde dicho contador es actualizado periódicamente por uno de los guardianes con una primera frecuencia predeterminada, y el otro guardián verifica dicha actualización con una segunda frecuencia predeterminada, determinando la existencia de una condición de fallo cuando el tiempo transcurrido desde la última actualización supera un umbral configurable, preferentemente de aproximadamente cinco segundos, y activando automáticamente, en respuesta a dicha condición de fallo, un protocolo de auto-regeneración del subsistema de seguridad sin intervención humana.

---

### Reivindicaciones Dependientes (Versión Detallada - Alternativa):

**Claim 3.1 (Dependiente de Claim 3):** El sistema de la reivindicación 3, donde el primer componente guardián actualiza el contador de tiempo compartido con una frecuencia de entre 100 y 500 milisegundos durante el procesamiento de eventos de kernel.

**Claim 3.2 (Dependiente de Claim 3):** El sistema de la reivindicación 3, donde el segundo componente guardián verifica el contador de tiempo compartido con una frecuencia de aproximadamente un segundo.

**Claim 3.3 (Dependiente de Claim 3):** El sistema de la reivindicación 3, donde el umbral predeterminado para activación del protocolo de auto-regeneración es de cinco segundos sin actualización del contador de tiempo.

**Claim 3.4 (Dependiente de Claim 3):** El sistema de la reivindicación 3, donde el protocolo de auto-regeneración comprende:
- Detección y registro de fallo del primer componente guardián;
- Recarga automática del programa eBPF asociado al primer componente guardián;
- Reinstalación de filtros de seguridad seccomp;
- Restauración de políticas de seguridad desde almacenamiento inmutable sellado criptográficamente;
- Generación de alerta al equipo de operaciones de seguridad;
- Resumir operaciones normales de monitoreo.

**Claim 3.5 (Dependiente de Claim 3):** El sistema de la reivindicación 3, donde el tiempo total de recuperación desde la detección de fallo hasta la reanudación de operaciones normales es inferior a siete segundos.

**Claim 3.6 (Dependiente de Claim 3):** El sistema de la reivindicación 3, donde el contador de tiempo compartido se implementa mediante una referencia atómica de conteo (Arc<AtomicU64>) en lenguaje Rust o mediante un mapa BPF de tipo BPF_MAP_TYPE_ARRAY en el kernel Linux.

**Claim 3.7 (Dependiente de Claim 3):** El sistema de la reivindicación 3, donde la vigilancia mutua es bidireccional, comprendiendo:
- Un primer latido emitido por el primer componente guardián y verificado por el segundo componente guardián;
- Un segundo latido emitido por el segundo componente guardián y verificado por el primer componente guardián.

**Claim 3.8 (Dependiente de Claim 3.7):** El sistema de la reivindicación 3.7, donde, en caso de fallo del segundo componente guardián detectado mediante ausencia del segundo latido, el primer componente guardián entra en un modo de operación degradado pero seguro, aplicando un conjunto restrictivo de reglas predefinidas a nivel de kernel sin confiar en decisiones procedentes del segundo componente guardián o de sistemas de inteligencia artificial.

**Claim 3.9 (Dependiente de Claim 3):** El sistema de la reivindicación 3, donde el almacenamiento inmutable para políticas de seguridad está sellado criptográficamente mediante un Módulo de Plataforma Confiable (TPM - Trusted Platform Module).

**Claim 3.10 (Dependiente de Claim 3):** El sistema de la reivindicación 3, donde el overhead de rendimiento del mecanismo de vigilancia mutua es inferior al 0.01% de utilización de CPU.

**Claim 3.11 (Dependiente de Claim 3):** El sistema de la reivindicación 3, donde el sistema está configurado para proteger plataformas de operaciones de inteligencia artificial (AIOps) contra ataques de inyección de telemetría que manipulan logs para ejecutar acciones maliciosas.

**Claim 3.12 (Dependiente de Claim 3):** El sistema de la reivindicación 3, donde la separación física entre el primer componente guardián (espacio de kernel, Ring 0) y el segundo componente guardián (espacio de usuario, Ring 3) proporciona aislamiento de privilegios que previene que un compromiso del segundo componente afecte directamente las capacidades de intercepción del primero.

---

## 📊 BLOQUE 3: MÉTODO (METHOD CLAIMS)

### Reivindicación de Método (Opcional - Amplía Protección):

**Claim 4 (Método Independiente):** Un método para monitoreo autónomo de seguridad en sistemas computacionales, que comprende los pasos de:

(a) Ejecutar un primer proceso de monitoreo en espacio de kernel que intercepta llamadas del sistema mediante programas eBPF;

(b) Ejecutar un segundo proceso de monitoreo en espacio de usuario que verifica integridad de configuraciones de seguridad;

(c) Mantener un contador de tiempo atómico compartido de 64 bits accesible por ambos procesos;

(d) Actualizar periódicamente dicho contador de tiempo mediante el primer proceso con una frecuencia de entre 100 y 500 milisegundos;

(e) Verificar periódicamente dicho contador de tiempo mediante el segundo proceso con una frecuencia de aproximadamente un segundo;

(f) Calcular el tiempo transcurrido desde la última actualización del contador;

(g) Determinar si el tiempo transcurrido excede un umbral de cinco segundos;

(h) En respuesta a determinar que el umbral ha sido excedido, activar automáticamente un protocolo de auto-regeneración que comprende:
   - Recargar el programa eBPF del primer proceso;
   - Reinstalar filtros de seguridad seccomp;
   - Restaurar políticas de seguridad desde almacenamiento inmutable;
   - Generar alerta al equipo de operaciones de seguridad;

(i) Resumir operaciones normales de monitoreo tras completar el protocolo de auto-regeneración, todo sin requerir intervención humana.

**Claim 4.1 (Dependiente de Claim 4):** El método de la reivindicación 4, donde el tiempo total desde la detección de fallo hasta la reanudación de operaciones normales es inferior a siete segundos.

**Claim 4.2 (Dependiente de Claim 4):** El método de la reivindicación 4, que además comprende:
- Emitir un segundo latido desde el segundo proceso;
- Verificar dicho segundo latido mediante el primer proceso;
- En respuesta a detectar ausencia del segundo latido, hacer que el primer proceso entre en un modo de operación degradado aplicando reglas restrictivas predefinidas a nivel de kernel.

---

## 📊 BLOQUE 4: LENGUAJE TÉCNICO ADICIONAL

### Para Sección "Detailed Description of the Invention":

**Heartbeat Mechanism - Implementación Detallada:**

En la realización preferente ilustrada en la Figura 2, el mecanismo de heartbeat se implementa mediante una estructura de datos atómica compartida entre el Guardian-Alpha (202) y el Guardian-Beta (204). Esta estructura puede ser un `Arc<AtomicU64>` en implementaciones basadas en Rust, o un mapa BPF de tipo `BPF_MAP_TYPE_ARRAY` con un único elemento de 64 bits en implementaciones puramente kernel-space.

El Guardian-Alpha actualiza este contador atómico durante cada ciclo de procesamiento de eventos eBPF. Específicamente, tras leer eventos del buffer de perf (`AsyncPerfEventArray`), el Guardian-Alpha ejecuta una operación de almacenamiento atómico (`atomic_store`) del timestamp Unix actual en el contador compartido. Esta operación utiliza ordenamiento relajado (`Ordering::Relaxed`) dado que la precisión absoluta del timestamp no es crítica para la detección de fallo, y este ordenamiento minimiza el overhead de sincronización de memoria.

El Guardian-Beta, ejecutándose en un bucle asíncrono con intervalo de un segundo, lee el valor del contador mediante una operación de carga atómica (`atomic_load`). Calcula el delta temporal como `current_time - last_heartbeat` y compara este valor contra el umbral de timeout (típicamente 5 segundos). Si el delta excede el umbral, el Guardian-Beta invoca la función `trigger_regenerative_protocol()`.

**Protocolo Regenerativo - Secuencia Detallada:**

El protocolo regenerativo ejecuta los siguientes pasos en secuencia:

1. **Logging Crítico:** Se registra un evento de nivel CRITICAL en el sistema de telemetría (Loki) con los siguientes campos:
   - `event_type`: "guardian_alpha_failure"
   - `last_heartbeat`: timestamp Unix de la última actualización
   - `delta_seconds`: tiempo transcurrido sin actualización
   - `trigger_timestamp`: timestamp Unix del momento de detección

2. **Recarga eBPF:** Se ejecuta el comando equivalente a `bpftool prog load` para recargar el programa eBPF desde el binario compilado almacenado en `/etc/sentinel/ebpf/guardian_alpha.o`. Este binario está protegido con permisos de solo lectura (0444) y checksums SHA-256 verificados contra valores almacenados en TPM.

3. **Reinstalación Seccomp:** Se reinstalan los filtros seccomp mediante llamadas a `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog)` con el programa de filtrado predefinido que bloquea syscalls críticas (execve, open, unlink, etc.) en modo `SECCOMP_RET_KILL_PROCESS`.

4. **Restauración de Políticas:** Se cargan las políticas de seguridad desde el archivo `/etc/sentinel/policies/guardian_alpha.policy`, cuyo hash SHA-256 está sellado en TPM y verificado antes de la carga.

5. **Reset de Heartbeat:** Se actualiza el contador atómico compartido con el timestamp actual para prevenir re-triggers inmediatos del protocolo regenerativo.

6. **Alerta:** Se envía una notificación al equipo de operaciones mediante webhook configurado, incluyendo detalles del fallo y acciones de recuperación tomadas.

El tiempo total de ejecución de este protocolo, medido en entornos de prueba con kernel Linux 5.15+, es de 1.8-2.2 segundos, resultando en un tiempo total de downtime (detección + regeneración) de 6.8-7.2 segundos.

**Modo Degradado Seguro - Comportamiento:**

En la realización bidireccional (Fase 2), cuando el Guardian-Alpha detecta ausencia del heartbeat del Guardian-Beta, entra en modo degradado aplicando las siguientes restricciones:

- Todas las decisiones de bloqueo/permiso se basan exclusivamente en una lista estática de denegación cargada en memoria del kernel
- No se consultan APIs externas ni sistemas de IA
- No se confía en decisiones procedentes del Guardian-Beta
- Se aplica política de "denegar por defecto" para syscalls no explícitamente permitidas
- Se genera alerta de degradación al equipo de operaciones

Este modo garantiza que, incluso con fallo total del Guardian-Beta, el sistema mantiene protección a nivel de kernel contra syscalls maliciosas, aunque con menor inteligencia contextual.

---

## 📋 CHECKLIST DE COMPLETITUD

### Bloques Listos para Patent Attorney:

- [x] **Resumen de la Invención** (Abstract/Summary)
  - [x] Descripción general del sistema
  - [x] Realización preferente
  - [x] Ventajas técnicas
  - [x] Aplicación práctica (AIOps protection)

- [x] **Reivindicación Independiente** (Claim 3)
  - [x] 5 elementos principales (a-e)
  - [x] Lenguaje claro y preciso

- [x] **Reivindicaciones Dependientes** (Claims 3.1-3.12)
  - [x] Frecuencias específicas (100-500ms, 1s, 5s)
  - [x] Protocolo regenerativo detallado
  - [x] Tiempo de recovery (< 7s)
  - [x] Implementación técnica (Arc<AtomicU64>, BPF map)
  - [x] Bidireccionalidad
  - [x] Modo degradado seguro
  - [x] TPM sealing
  - [x] Performance overhead (< 0.01%)
  - [x] Aplicación AIOps
  - [x] Separación física Ring 0/Ring 3

- [x] **Reivindicación de Método** (Claim 4)
  - [x] Pasos del método (a-i)
  - [x] Claims dependientes de método

- [x] **Descripción Detallada**
  - [x] Implementación de heartbeat
  - [x] Secuencia de protocolo regenerativo
  - [x] Modo degradado seguro

---

##  PRÓXIMOS PASOS

### Para el Patent Attorney:

1. **Revisar y ajustar** el lenguaje legal según preferencias del attorney
2. **Integrar** estos bloques en el draft de provisional patent
3. **Crear figuras** (Figura 2: Diagrama de heartbeat bidireccional)
4. **Validar** que las reivindicaciones dependientes cubren todas las variaciones importantes

### Opciones de Expansión (Si el Attorney lo Recomienda):

- [ ] Reivindicaciones adicionales para TPM sealing específico
- [ ] Reivindicaciones para implementación en contenedores/Kubernetes
- [ ] Reivindicaciones para aplicación específica en AIOps/SOAR
- [ ] Reivindicaciones de sistema de computación (computer system claims)

---

**Documento:** Patent Filing - Additional Blocks  
**Status:** ✅ LEGAL LANGUAGE READY  
**Bloques:** 4 (Resumen, Claims Dependientes, Método, Descripción Detallada)  
**Total Claims:** 1 independiente + 12 dependientes + 1 método + 2 método dependientes = **16 claims**  
**Next Action:** Enviar a patent attorney para integración en draft
