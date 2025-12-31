"""
Cortex Decision Engine

Main service that orchestrates security event processing:
1. Event validation and enrichment
2. Pattern detection
3. Confidence scoring
4. Decision making
5. Escalation to Guardian Gamma when needed
"""

from typing import Dict, Any
import logging
from datetime import datetime
from time import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.cortex_event import CortexEvent
from app.models.cortex_decision import CortexDecision
from app.models.security_pattern import SecurityPattern
from app.services.pattern_detector import PatternDetector
from app.services.confidence_scorer import ConfidenceScorer
from app.security.aiops_shield import AIOpsShield
from app.services.metrics_service import (
    CORTEX_PROCESSING_TIME,
    CORTEX_PATTERNS_TOTAL,
    CORTEX_DECISIONS_TOTAL,
    CORTEX_ERRORS_TOTAL,
    track_time
)

logger = logging.getLogger(__name__)

# Umbral máximo de tiempo de procesamiento permitido antes de Fail-Closed (TOCTOU Defense)
MAX_SAFE_PROCESS_TIME_MS = 100.0

# Umbral de eventos por segundo para detectar inundación (Ring Wrap-around Defense)
MAX_EVENTS_PER_SECOND = 100


class CortexDecisionEngine:
    """
    Main Cortex Decision Engine
    
    Processes security events and makes intelligent decisions
    using pattern detection and confidence scoring.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize Cortex Engine
        
        Args:
            db: Database session
        """
        self.db = db
        self.pattern_detector = PatternDetector(db)
        self.confidence_scorer = ConfidenceScorer()
        self.guardian_heartbeats = {"guardian_alpha": time(), "guardian_beta": time()} # Simulación multi-guardián
        self.autoinmune_mode = False
    
    @track_time(CORTEX_PROCESSING_TIME)
    async def process_event(self, event_data: Dict[str, Any]) -> CortexDecision:
        """
        Procesa un evento de seguridad y toma una decisión inteligente.
        """
        start_time_total = time()
        
        # ACT 1: Cognitive Hardening (AIOpsShield)
        # Prevent AIOpsDoom by blocking toxic logs before they reach the engine
        if not AIOpsShield.sanitize_log(event_data):
            logger.warning(f"🛡️ AIOpsShield: Event QUARANTINED due to AIOpsDoom pattern.")
            # Create a synthetic decision for quarantine
            decision = CortexDecision(
                event_id=None, # Will be set or handled below if we want to save it
                decision_type="quarantine",
                confidence=1.0,
                patterns_detected=["AIOpsDoom"],
                reasoning="AIOpsShield: Potential cognitive injection (AIOpsDoom) detected in telemetry logs. Event blocked from LLM processing.",
                processing_time_ms=(time() - start_time_total) * 1000
            )
            # We still want to save the event for forensics
            enriched_event = await self._enrich_event(event_data)
            db_event = await self._save_event(enriched_event)
            decision.event_id = db_event.id
            
            self.db.add(decision)
            await self.db.commit()
            return decision

        try:
            # MECANISMO DE INTEGRIDAD DE VERDAD (Ring Wrap-around Defense)
            # Monitorear la tasa de eventos para detectar inundaciones que oculten exploits
            # (Simulado: en prod esto leería flags de overflow del ring buffer eBPF)
            if self._is_ring_overloaded():
                logger.error("🛑 TRUTH INCONSISTENCY: Posible Ring Buffer Wrap-around detectado. Datos comprometidos.")
                event_data["risk_score"] = 1.0
                event_data["truth_compromised"] = True
            
            # Paso 1: Validar y enriquecer evento
            enriched_event = await self._enrich_event(event_data)
            
            # Paso 2: Guardar evento en la DB
            db_event = await self._save_event(enriched_event)
            
            # Paso 3: Detectar patrones (ahora devuelve objetos SecurityPattern)
            detected_patterns = await self.pattern_detector.detect(enriched_event)
            pattern_names = [p.name for p in detected_patterns]
            
            # Registrar métricas de patrones detectados
            for p in detected_patterns:
                CORTEX_PATTERNS_TOTAL.labels(
                    pattern_type=p.name,
                    severity=p.severity
                ).inc()
            
            # Paso 4: Calcular confianza
            confidence = await self.confidence_scorer.score(enriched_event, pattern_names)
            
            # Paso 5: Tomar decisión
            decision_type = self.confidence_scorer.get_decision_type(confidence)
            reasoning = self.confidence_scorer.generate_reasoning(
                enriched_event, pattern_names, confidence
            )
            
            # Registrar métrica de decisión
            CORTEX_DECISIONS_TOTAL.labels(decision_type=decision_type).inc()
            
            # Paso 6: Calcular tiempo de procesamiento real
            p_time_ms = (time() - start_time_total) * 1000
            
            # MECANISMO FAIL-CLOSED (Defensa TOCTOU)
            # Si el procesamiento ha sido demasiado lento, bloqueamos preventivamente
            if p_time_ms > MAX_SAFE_PROCESS_TIME_MS:
                logger.warning(f"⚠️ FAIL-CLOSED ACTIVADO: Procesamiento lento ({p_time_ms:.1f}ms > {MAX_SAFE_PROCESS_TIME_MS}ms). Bloqueo preventivo.")
                decision_type = "block"
                reasoning = f"SEC_FAIL_CLOSED - Processing latency ({p_time_ms:.1f}ms) exceeded safety threshold to prevent TOCTOU attack."
            
            # Paso 7: Crear objeto de decisión
            decision = CortexDecision(
                event_id=db_event.id,
                decision_type=decision_type,
                confidence=confidence,
                patterns_detected=pattern_names,
                reasoning=reasoning,
                processing_time_ms=p_time_ms
            )
            
            self.db.add(decision)
            await self.db.commit()
            await self.db.refresh(decision)
            
            # Paso 8: Escalar a Guardian Gamma si es necesario
            if decision_type == "escalate":
                await self._escalate_to_gamma(decision, enriched_event)
            
            # BROADCAST REAL-TIME EVENT (Battlefield UI)
            # Enviar el evento y decisión al sistema de visualización vía WebSocket
            try:
                from app.managers.connection_manager import manager
                import json
                
                # Serializar para el frontend
                ws_message = {
                    "type": "decision",
                    "data": {
                        "id": decision.id,
                        "decision_type": decision.decision_type,
                        "confidence": decision.confidence,
                        "patterns": decision.patterns_detected,
                        "process": enriched_event.get("process_name"),
                        "timestamp": enriched_event.get("timestamp"),
                        "latency_ms": p_time_ms
                    }
                }
                await manager.broadcast(json.dumps(ws_message))
            except Exception as e:
                logger.error(f"⚠️ Failed to broadcast WebSocket event: {e}")
                # No fallar el procesamiento principal por error de UI

            return decision
            
        except Exception as e:
            CORTEX_ERRORS_TOTAL.labels(error_type=type(e).__name__).inc()
            logger.error(f"❌ Error procesando evento en Cortex: {e}", exc_info=True)
            await self.db.rollback()
            raise
            
        except Exception as e:
            logger.error(f"❌ Error processing event: {e}", exc_info=True)
            await self.db.rollback()
            raise
    
    async def _enrich_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event with additional context
        
        Args:
            event_data: Raw event data
        
        Returns:
            Enriched event data
        """
        enriched = event_data.copy()
        
        # Add timestamp if not present (as ISO string for JSON serialization)
        if "timestamp" not in enriched:
            enriched["timestamp"] = datetime.utcnow().isoformat()
        
        # Extract process name from path if available
        if "process_path" in enriched and "process_name" not in enriched:
            process_path = enriched["process_path"]
            enriched["process_name"] = process_path.split("/")[-1]
        
        # Determine if network destination is external
        if enriched.get("event_type") == "network":
            dest_ip = enriched.get("dest_ip", "")
            enriched["is_external"] = self._is_external_ip(dest_ip)
            enriched["is_internal"] = not enriched["is_external"]
        
        # Calculate initial risk score based on event type
        enriched["risk_score"] = self._calculate_initial_risk(enriched)
        
        return enriched
    
    async def _save_event(self, event_data: Dict[str, Any]) -> CortexEvent:
        """
        Save event to database
        
        Args:
            event_data: Enriched event data
        
        Returns:
            Saved CortexEvent object
        """
        event = CortexEvent(
            event_type=event_data.get("event_type", "unknown"),
            source=event_data.get("source", "unknown"),
            raw_data=event_data,
            process_name=event_data.get("process_name"),
            process_path=event_data.get("process_path"),
            user=event_data.get("user"),
            pid=event_data.get("pid"),
            ppid=event_data.get("ppid"),
            risk_score=event_data.get("risk_score", 0.0)
        )
        
        self.db.add(event)
        await self.db.flush()  # Get ID without committing
        
        return event
    
    async def _escalate_to_gamma(
        self,
        decision: CortexDecision,
        event_data: Dict[str, Any]
    ) -> None:
        """
        Escalate decision to Guardian Gamma (Human-in-the-Loop)
        
        Args:
            decision: The decision to escalate
            event_data: Event data for context
        """
        try:
            # Import here to avoid circular dependency
            from app.services.guardian_gamma import GuardianGammaService, GuardianSource, DecisionType
            
            gamma_service = GuardianGammaService(self.db)
            
            # Map decision to Gamma decision type
            decision_type_map = {
                "block": DecisionType.BINARY_BLOCK,
                "escalate": DecisionType.ESCALATED,
                "allow": DecisionType.ALLOW
            }
            
            gamma_decision_type = decision_type_map.get(
                decision.decision_type,
                DecisionType.BINARY_BLOCK
            )
            
            # Create context for human review
            context = {
                "event_type": event_data.get("event_type"),
                "process_path": event_data.get("process_path"),
                "user": event_data.get("user"),
                "patterns_detected": decision.patterns_detected,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning
            }
            
            # Create Gamma decision
            gamma_id = await gamma_service.create_decision(
                guardian=GuardianSource.ALPHA,  # Assume Alpha for now
                decision_type=gamma_decision_type,
                context=context,
                confidence=decision.confidence,
                evidence=event_data,
                timeout_minutes=30
            )
            
            # Link to Cortex decision
            decision.escalated_to_gamma = gamma_id
            await self.db.commit()
            
            logger.info(
                f"📤 Escalated decision {decision.id} to Guardian Gamma "
                f"(gamma_id: {gamma_id})"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to escalate to Gamma: {e}", exc_info=True)
            # Don't fail the whole decision if escalation fails
    
    def _is_external_ip(self, ip: str) -> bool:
        """
        Check if an IP address is external (not private)
        
        Args:
            ip: IP address string
        
        Returns:
            True if external
        """
        if not ip:
            return False
        
        # Private IP ranges
        private_ranges = [
            "10.",
            "172.16.", "172.17.", "172.18.", "172.19.",
            "172.20.", "172.21.", "172.22.", "172.23.",
            "172.24.", "172.25.", "172.26.", "172.27.",
            "172.28.", "172.29.", "172.30.", "172.31.",
            "192.168.",
            "127.",
            "localhost"
        ]
        
        return not any(ip.startswith(prefix) for prefix in private_ranges)
    
    def _calculate_initial_risk(self, event_data: Dict[str, Any]) -> float:
        """
        Calculate initial risk score based on event characteristics
        
        Args:
            event_data: Event data
        
        Returns:
            Risk score (0.0 - 1.0)
        """
        risk = 0.0
        
        # Event type risk
        event_type = event_data.get("event_type", "")
        type_risk = {
            "syscall": 0.3,
            "network": 0.2,
            "memory": 0.4,
            "file": 0.1
        }
        risk += type_risk.get(event_type, 0.1)
        
        # Root user increases risk
        if event_data.get("uid") == 0:
            risk += 0.2
        
        # External network increases risk
        if event_data.get("is_external"):
            risk += 0.3
        
        return min(1.0, risk)
    
    async def get_recent_decisions(
        self,
        limit: int = 100,
        decision_type: str = None
    ) -> list[CortexDecision]:
        """
        Get recent decisions
        
        Args:
            limit: Maximum number of decisions to return
            decision_type: Filter by decision type (optional)
        
        Returns:
            List of CortexDecision objects
        """
        query = select(CortexDecision).order_by(CortexDecision.created_at.desc())
        
        if decision_type:
            query = query.where(CortexDecision.decision_type == decision_type)
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get Cortex Engine statistics
        
        Args:
            hours: Time window in hours
        
        Returns:
            Statistics dictionary
        """
        from datetime import timedelta
        from sqlalchemy import func
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Count decisions by type
        result = await self.db.execute(
            select(
                CortexDecision.decision_type,
                func.count(CortexDecision.id).label("count"),
                func.avg(CortexDecision.confidence).label("avg_confidence"),
                func.avg(CortexDecision.processing_time_ms).label("avg_time_ms")
            )
            .where(CortexDecision.created_at >= cutoff)
            .group_by(CortexDecision.decision_type)
        )
        
        stats_by_type = {row[0]: {
            "count": row[1],
            "avg_confidence": float(row[2]) if row[2] else 0.0,
            "avg_processing_time_ms": float(row[3]) if row[3] else 0.0
        } for row in result}
        
        # Total events
        total_result = await self.db.execute(
            select(func.count(CortexEvent.id))
            .where(CortexEvent.timestamp >= cutoff)
        )
        total_events = total_result.scalar()
        
        return {
            "time_window_hours": hours,
            "total_events": total_events,
            "decisions_by_type": stats_by_type,
            "total_decisions": sum(s["count"] for s in stats_by_type.values())
        }

    def detect_guardian_failure(self) -> str:
        """
        Detección de "Ceguera de Guardianes" (Chaos Engineering).
        Si un Guardián no reporta latido en > 500ms, se activa el Fail-Closed.
        """
        now = time()
        for guardian, last_beat in self.guardian_heartbeats.items():
            if now - last_beat > 0.5: # 500ms de gracia
                self.autoinmune_mode = True
                return guardian
        return None

    def _is_ring_overloaded(self) -> bool:
        """
        Detecta si el sistema de telemetría está bajo un ataque de inundación.
        (Mecánica simulada para el Hackathon Global).
        """
        # Si estamos en modo autoinmune por fallo de guardian, forzar alerta
        if self.autoinmune_mode:
            return True
        return False # Cambiar a True manualmente durante PoC
