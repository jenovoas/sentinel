#!/usr/bin/env bash
# -------------------------------------------------------------------------------------
# MYCNET: CEPH YHWH TUNER
# Modula el comportamiento de Ceph (backfills y recovery) basado en el patrón YHWH.
# Patrón: Yod(10) -> He(5) -> Vav(6) -> He(5)
# -------------------------------------------------------------------------------------

PATTERN=(10 5 6 5)
HOUR=$(date +%H)
# Determinar la fase (cambia cada 6 horas)
PHASE=$(( (10#$HOUR / 6) % 4 ))
FACTOR=${PATTERN[$PHASE]}

echo "--- MYCNET: YHWH CEPH TUNER ---"
echo "Hora actual: $HOUR:00 | Fase YHWH: $PHASE | Factor: $FACTOR"

# Modular backfills según el factor de la fase actual
if [ "$FACTOR" -ge 10 ]; then
  # Fase Yod: Alta energía, permitimos rebalanceo más agresivo
  BACKFILLS=2
  SLEEP=0.05
  MODE="AGRESIVO"
else
  # Fases He/Vav: Energía de mantenimiento, límites conservadores para priorizar latencia
  BACKFILLS=1
  SLEEP=0.20
  MODE="CONSERVADOR"
fi

echo "Modo detectado: $MODE"
echo "Configurando osd_max_backfills = $BACKFILLS"
echo "Configurando osd_recovery_sleep = $SLEEP"

# Aplicar configuración al cluster de Ceph
ceph config set osd osd_max_backfills "$BACKFILLS"
ceph config set osd osd_recovery_sleep "$SLEEP"

echo "✅ Sincronización YHWH completada."
