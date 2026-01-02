"""
OpenAPI/Swagger Documentation Generator for Sentinel
=====================================================

This script generates comprehensive OpenAPI 3.0 documentation for Sentinel's API.

Usage:
    python generate_openapi.py > openapi.yaml
"""

import yaml
from typing import Dict, Any

def generate_openapi_spec() -> Dict[str, Any]:
    """Generate complete OpenAPI 3.0 specification"""
    
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Sentinel API",
            "description": "Advanced Intelligence Platform for Scientific Research",
            "version": "2.1.0",
            "contact": {
                "name": "Sentinel Team",
                "email": "research@sentinel.ai",
                "url": "https://github.com/yourusername/sentinel"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Local development server"
            },
            {
                "url": "https://api.sentinel.ai",
                "description": "Production server"
            }
        ],
        "tags": [
            {"name": "Health", "description": "System health and status endpoints"},
            {"name": "AI", "description": "AI query and analysis endpoints"},
            {"name": "TruthSync", "description": "Claim verification endpoints"},
            {"name": "Analytics", "description": "Analytics and metrics endpoints"},
            {"name": "Dashboard", "description": "Dashboard data endpoints"}
        ],
        "paths": {
            "/api/v1/health": {
                "get": {
                    "tags": ["Health"],
                    "summary": "Get system health",
                    "description": "Returns overall system health status including component health checks",
                    "operationId": "getHealth",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HealthResponse"},
                                    "example": {
                                        "status": "healthy",
                                        "timestamp": "2026-01-02T12:00:00.000000",
                                        "uptime_seconds": 3600.5,
                                        "role": "standby",
                                        "components": {
                                            "database": {
                                                "status": "healthy",
                                                "latency_ms": 5.2,
                                                "is_primary": True,
                                                "host": "postgres"
                                            },
                                            "redis": {
                                                "status": "healthy",
                                                "latency_ms": 1.5,
                                                "mode": "sentinel"
                                            },
                                            "ollama": {
                                                "status": "healthy",
                                                "latency_ms": 50.3,
                                                "enabled": True
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/dashboard/status": {
                "get": {
                    "tags": ["Dashboard"],
                    "summary": "Get detailed system status",
                    "description": "Returns detailed system metrics including CPU, memory, network, and semantic vectors",
                    "operationId": "getDashboardStatus",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/StatusResponse"},
                                    "example": {
                                        "cpu": "15.2",
                                        "memory": "42.8",
                                        "uptime": 3600,
                                        "coherence": 0.96,
                                        "entropy": 0.073,
                                        "tte_us": 3.23,
                                        "network": {
                                            "rx_bytes_sec": "1024000",
                                            "tx_bytes_sec": "512000"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/ai/query": {
                "post": {
                    "tags": ["AI"],
                    "summary": "Query AI model",
                    "description": "Send a prompt to the AI model and receive a response",
                    "operationId": "queryAI",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AIQueryRequest"},
                                "example": {
                                    "prompt": "Explain quantum computing",
                                    "max_tokens": 100,
                                    "temperature": 0.3
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AIQueryResponse"},
                                    "example": {
                                        "response": "Quantum computing uses quantum mechanical phenomena...",
                                        "model": "phi3:mini",
                                        "enabled": True
                                    }
                                }
                            }
                        },
                        "403": {
                            "description": "Malicious prompt detected",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "500": {
                            "description": "AI service error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/ai/health": {
                "get": {
                    "tags": ["AI"],
                    "summary": "Get AI service health",
                    "description": "Returns AI service status and available models",
                    "operationId": "getAIHealth",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AIHealthResponse"},
                                    "example": {
                                        "status": "healthy",
                                        "enabled": True,
                                        "url": "http://ollama:11434",
                                        "model": "phi3:mini",
                                        "models_available": ["phi3:mini", "llama3.2:3b", "qwen2.5-coder:3b"]
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/truthsync/verify": {
                "post": {
                    "tags": ["TruthSync"],
                    "summary": "Verify a claim",
                    "description": "Verify a text claim using TruthSync protocol",
                    "operationId": "verifyClaim",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/VerificationRequest"},
                                "example": {
                                    "text": "Water boils at 100°C at sea level",
                                    "metadata": {
                                        "source": "research_data",
                                        "layer": "verification"
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/VerificationResponse"},
                                    "example": {
                                        "text": "Water boils at 100°C at sea level",
                                        "confidence": 0.95,
                                        "status": "VERIFIED",
                                        "claims": ["Water boiling point verified"],
                                        "processing_time_us": 1250,
                                        "cache_hit": False
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/truthsync/health": {
                "get": {
                    "tags": ["TruthSync"],
                    "summary": "Get TruthSync health",
                    "description": "Returns TruthSync service health status",
                    "operationId": "getTruthSyncHealth",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/TruthSyncHealthResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/analytics/statistics": {
                "get": {
                    "tags": ["Analytics"],
                    "summary": "Get analytics statistics",
                    "description": "Returns analytics data for specified time period",
                    "operationId": "getAnalyticsStatistics",
                    "parameters": [
                        {
                            "name": "hours",
                            "in": "query",
                            "description": "Number of hours of historical data",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "default": 24,
                                "minimum": 1,
                                "maximum": 168
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AnalyticsResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/analytics/anomalies": {
                "get": {
                    "tags": ["Analytics"],
                    "summary": "Get detected anomalies",
                    "description": "Returns list of detected system anomalies",
                    "operationId": "getAnomalies",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Anomaly"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "HealthResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["healthy", "degraded", "unhealthy"]},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "uptime_seconds": {"type": "number"},
                        "role": {"type": "string"},
                        "components": {
                            "type": "object",
                            "properties": {
                                "database": {"$ref": "#/components/schemas/ComponentHealth"},
                                "redis": {"$ref": "#/components/schemas/ComponentHealth"},
                                "ollama": {"$ref": "#/components/schemas/ComponentHealth"}
                            }
                        }
                    }
                },
                "ComponentHealth": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "latency_ms": {"type": "number"},
                        "enabled": {"type": "boolean"}
                    }
                },
                "StatusResponse": {
                    "type": "object",
                    "properties": {
                        "cpu": {"type": "string", "description": "CPU usage percentage"},
                        "memory": {"type": "string", "description": "Memory usage percentage"},
                        "uptime": {"type": "number", "description": "System uptime in seconds"},
                        "coherence": {"type": "number", "minimum": 0, "maximum": 1},
                        "entropy": {"type": "number"},
                        "tte_us": {"type": "number", "description": "Time-to-equilibrium in microseconds"},
                        "network": {
                            "type": "object",
                            "properties": {
                                "rx_bytes_sec": {"type": "string"},
                                "tx_bytes_sec": {"type": "string"}
                            }
                        }
                    }
                },
                "AIQueryRequest": {
                    "type": "object",
                    "required": ["prompt"],
                    "properties": {
                        "prompt": {"type": "string", "description": "Text prompt for AI"},
                        "max_tokens": {"type": "integer", "default": 100, "minimum": 10, "maximum": 500},
                        "temperature": {"type": "number", "default": 0.3, "minimum": 0.0, "maximum": 1.0}
                    }
                },
                "AIQueryResponse": {
                    "type": "object",
                    "properties": {
                        "response": {"type": "string"},
                        "model": {"type": "string"},
                        "enabled": {"type": "boolean"}
                    }
                },
                "AIHealthResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "enabled": {"type": "boolean"},
                        "url": {"type": "string"},
                        "model": {"type": "string"},
                        "models_available": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "VerificationRequest": {
                    "type": "object",
                    "required": ["text"],
                    "properties": {
                        "text": {"type": "string", "description": "Text to verify"},
                        "metadata": {"type": "object", "additionalProperties": True}
                    }
                },
                "VerificationResponse": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "status": {"type": "string"},
                        "claims": {"type": "array", "items": {"type": "string"}},
                        "processing_time_us": {"type": "number"},
                        "cache_hit": {"type": "boolean"}
                    }
                },
                "TruthSyncHealthResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "enabled": {"type": "boolean"}
                    }
                },
                "AnalyticsResponse": {
                    "type": "object",
                    "properties": {
                        "period_hours": {"type": "integer"},
                        "metrics": {"type": "array", "items": {"type": "object"}}
                    }
                },
                "Anomaly": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "type": {"type": "string"},
                        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                        "description": {"type": "string"},
                        "metric_value": {"type": "number"},
                        "threshold_value": {"type": "number"}
                    }
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                        "detail": {"type": "string"},
                        "status_code": {"type": "integer"}
                    }
                }
            },
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "API key for authentication (if enabled)"
                }
            }
        }
    }
    
    return spec


if __name__ == "__main__":
    spec = generate_openapi_spec()
    print(yaml.dump(spec, default_flow_style=False, sort_keys=False))
