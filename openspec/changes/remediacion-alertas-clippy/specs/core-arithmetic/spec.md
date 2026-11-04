# Spec Delta

## Purpose

Define el contrato observable de aritmética del core para preservar resultados S60 exactos y evitar conversiones numéricas silenciosamente destructivas.

## ADDED Requirements

### Requirement: La lógica numérica central usa S60 entero

El core SHALL representar y calcular valores numéricos operativos con enteros S60, sin operaciones de punto flotante binario.

#### Scenario: Cálculo numérico operativo
- **WHEN** el core calcula, compara o actualiza un valor numérico de dominio
- **THEN** el resultado se obtiene mediante representación entera S60 sin conversión intermedia a punto flotante binario

### Requirement: Las conversiones numéricas verifican su rango

El core SHALL rechazar o acotar explícitamente una conversión que no quepa en el tipo destino, y MUST no depender de un cast que descarte bits silenciosamente.

#### Scenario: Valor representable
- **WHEN** un valor de origen cabe en el tipo destino
- **THEN** la conversión conserva exactamente su valor entero

#### Scenario: Valor fuera de rango
- **WHEN** un valor de origen excede el rango permitido por el tipo destino
- **THEN** la operación devuelve un error o aplica el límite definido por el contrato de esa operación, sin envoltura ni truncamiento implícito
