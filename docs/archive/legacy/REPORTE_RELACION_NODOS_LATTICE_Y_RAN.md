# 📡 Principio de Escala: Relación entre Nodos de la Rejilla y la Capa RAN

> **Módulo:** `HexagonalController` (`me60os_core::hexagonal_control`) & `ResonantLatticeBridge`  
> **Fecha:** 29 de Julio, 2026  
> **Estado:** 🟢 **PRINCIPIO ARQUITECTÓNICO CONFIRMADO**

---

## 📡 1. Mapeo Físico y Topológico (RAM / RAM-Nodos)

El número total de nodos de la Rejilla Resonante ($N_{\text{nodes}}$) no es una constante arbitraria hardcodeada, sino una función directa de la infraestructura de hardware y radioacceso (**RAN / Radio Access Network** / Celdas Hexagonales):

1. **Topología de Cobertura Hexagonal**:
   En la geometría de empaquetamiento hexagonal compacto ($3r^2 - 3r + 1$):
   - **Radio 1 (Pilar Básico):** $3(1)^2 - 3(1) + 1 = 1$ nodo.
   - **Radio 7 (Pilar Hexagonal 91 Nodos):** $3(7)^2 - 3(7) + 1 = 91$ nodos.
   - **Dual-Lane 128 Nodos:** 64 Nodos Security Lane + 64 Nodos Observability Lane.

2. **Dinamismo según la Capa RAN**:
   A medida que la red escala (agregando celdas RAN, interfaces físicas de red o unidades de cómputo dispersas en la Malla ADM), la dimensión del cristal se expande biyectivamente para alojar $1$ nodo de cristal por cada unidad de radioacceso/celda física.

