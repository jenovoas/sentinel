# Paso 4 listo para aplicar tras política paso 3.
# Drop-in systemd para sentinel-security-gateway en Marte.
# NO APLICAR hasta que Jaime defina whitelist AI/Float (paso 3).

# Instalar en Marte: /etc/systemd/system/sentinel-security-gateway.service.d/ebpf-paths.conf
# Contenido:
#
# [Service]
# Environment="EBPF_EVENTS_PATHS=/sys/fs/bpf/guardian_alpha/events=2"
#
# Tras cargar ai_guardian + float_detector (paso 2+3), ampliar a:
# Environment="EBPF_EVENTS_PATHS=/sys/fs/bpf/guardian_alpha/events=2,/sys/fs/bpf/guardian_alpha/ai_events=3,/sys/fs/bpf/guardian_alpha/float_events=4"
#
# Códigos: 1=alpha 2=cognitive 3=ai 4=float 5=gamma (guardian_source en gateway).
# gamma_watchdog emite NDJSON a stdout (journald), no ringbuf: no va en PATHS.
#
# Validación paso 5:
#   journalctl -u sentinel-security-gateway | grep -i "guardian_code"
#   POST /api/v1/cortex/events en Fenix con X-Sentinel-Token
#   /health QHC + bio_portal_open tras drive eBPF real
