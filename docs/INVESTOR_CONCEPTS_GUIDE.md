# 📚 Guía Completa de Conceptos - Sentinel para Inversores

## Introducción

Jaime, esta guía te prepara para **dominar** todas las conversaciones con inversores. Cada concepto explicado de forma simple y práctica.

---

## PARTE 1: Conceptos de Fundraising (Levantamiento de Capital)

### 1.1 ¿Qué es una Ronda Seed?

**Definición simple**: La primera inversión "seria" que recibe una startup.

**Características**:
- **Monto**: $500K - $5M USD (típicamente $1-3M)
- **Etapa**: Tienes MVP, buscas primeros clientes
- **Uso**: Contratar equipo, validar mercado
- **Equity**: Das 10-20% de la empresa
- **Timeline**: 3-6 meses de fundraising

**Ejemplo práctico**:
```
Levantas: $2M USD
Das: 15% de la empresa
Valuación: $2M / 0.15 = $13.3M (post-money)
Usas para: 3 ingenieros ($400K) + ops ($600K) + runway 18 meses
```

### 1.2 ¿Qué es un Pitch Deck?

**Definición**: Presentación de 10-15 slides que cuenta tu historia.

**Objetivo**: Conseguir una reunión de 30 minutos con el VC.

**Estructura estándar**:
1. **Cover**: Logo + tagline
2. **Problem**: ¿Qué duele?
3. **Solution**: Tu producto
4. **Market**: ¿Qué tan grande?
5. **Product**: Demo/screenshots
6. **Business Model**: ¿Cómo ganas dinero?
7. **Traction**: ¿Qué has logrado?
8. **Competition**: ¿Por qué tú?
9. **Team**: ¿Quién ejecuta?
10. **Ask**: ¿Cuánto necesitas?

**Regla de oro**: 1 idea por slide, máximo 50 palabras.

### 1.3 ¿Qué es TAM/SAM/SOM?

**TAM (Total Addressable Market)**: Todo el mercado posible
- Ejemplo: $50B (todo el mercado de observability + security)

**SAM (Serviceable Available Market)**: Tu segmento realista
- Ejemplo: $10B (empresas 50-500 empleados)

**SOM (Serviceable Obtainable Market)**: Lo que puedes capturar
- Ejemplo: $500M (self-hosted segment en 5 años)

**Por qué importa**: Inversores quieren mercados de $1B+ (TAM).

### 1.4 ¿Qué es ARR/MRR?

**MRR (Monthly Recurring Revenue)**: Ingresos mensuales recurrentes
- Ejemplo: 50 clientes x $800/mes = $40K MRR

**ARR (Annual Recurring Revenue)**: MRR x 12
- Ejemplo: $40K x 12 = $480K ARR

**Por qué importa**: SaaS se valúa por ARR (típicamente 10-20x ARR).

**Ejemplo**:
```
$2M ARR x 15 (múltiplo) = $30M valuación (Series A)
```

### 1.5 ¿Qué es CAC/LTV?

**CAC (Customer Acquisition Cost)**: Costo de conseguir 1 cliente
- Ejemplo: $5K (marketing + sales + tiempo)

**LTV (Lifetime Value)**: Valor total de 1 cliente
- Ejemplo: $800/mes x 36 meses = $28.8K

**Ratio ideal**: LTV/CAC > 3
- Tu caso: $28.8K / $5K = 5.76 ✅ (excelente)

**Por qué importa**: Demuestra que el negocio es rentable.

### 1.6 ¿Qué es Churn?

**Definición**: % de clientes que cancelan cada mes.

**Cálculo**:
```
Churn = (Clientes perdidos / Clientes totales) x 100
```

**Ejemplo**:
- Mes 1: 100 clientes
- Mes 2: 3 cancelan
- Churn = 3/100 = 3%

**Benchmark**:
- Excelente: <3%
- Bueno: 3-5%
- Malo: >5%

**Por qué importa**: Churn alto = negocio insostenible.

---

## PARTE 2: Conceptos Técnicos (Arquitectura)

### 2.1 ¿Qué es High Availability (HA)?

**Definición simple**: Tu sistema sigue funcionando aunque algo falle.

**Componentes**:
1. **Redundancia**: 2+ servidores haciendo lo mismo
2. **Failover**: Si uno cae, otro toma el control
3. **Load Balancing**: Distribuir carga entre servidores

**Tu caso (Sentinel)**:
```
Nodo 1 (On-prem) ←→ Nodo 2 (Cloud standby)
   ↓ Si falla
Nodo 2 toma control automáticamente (Patroni)
```

**Uptime**:
- Sin HA: 99% (3.65 días down/año)
- Con HA: 99.99% (52 minutos down/año)

**Por qué importa**: Empresas pagan más por HA (menos downtime = menos pérdidas).

### 2.2 ¿Qué es CDN + WAF?

**CDN (Content Delivery Network)**: Red de servidores que cachea tu contenido cerca del usuario.

**Ejemplo**: Cloudflare
- Usuario en Chile → Servidor en Santiago (rápido)
- Usuario en USA → Servidor en Miami (rápido)

**WAF (Web Application Firewall)**: Firewall que bloquea ataques web.

**Protege contra**:
- SQL Injection
- XSS (Cross-Site Scripting)
- DDoS (Distributed Denial of Service)

**Tu estrategia "Black Hole"**:
```
Internet → Cloudflare (IP pública) → Tu servidor (IP oculta)
Atacante solo ve Cloudflare, no puede atacar directamente
```

### 2.3 ¿Qué es AI Local (On-Premise)?

**Definición**: La IA corre en TU servidor, no en la nube.

**Ventajas**:
1. **Privacy**: Datos nunca salen de tu infraestructura
2. **Compliance**: GDPR/CCPA automático
3. **Costo**: $0/mes (vs $0.01/token en OpenAI)
4. **Latencia**: <100ms (vs 500ms+ en cloud)

**Tu caso (Ollama + Phi-3)**:
```
Logs → Ollama (local) → Análisis → Dashboard
Todo en casa, nada sale a internet
```

**Por qué importa**: Bancos, gobiernos, healthcare necesitan esto (compliance).

### 2.4 ¿Qué es Self-Healing?

**Definición**: Sistema que se repara solo cuando detecta problemas.

**Ejemplo**:
```
1. Detecta: Servidor comprometido (malware)
2. Decide: Nuke & Pave (formatear)
3. Ejecuta: PXE Boot → Reinstala desde imagen limpia
4. Resultado: Servidor limpio en 10 minutos
```

**Tecnologías**:
- **PXE Boot**: Arranque desde red
- **Imágenes inmutables**: Sistema operativo "congelado"
- **Ansible/Terraform**: Automatización

**Por qué importa**: Reduce tiempo de recuperación de horas a minutos.

### 2.5 ¿Qué es Patroni + etcd?

**Patroni**: Gestor de HA para PostgreSQL
- Monitorea salud de base de datos
- Hace failover automático
- Elige nuevo "líder" si el actual cae

**etcd**: Base de datos distribuida para configuración
- Almacena: ¿Quién es el líder?
- Consenso: Todos los nodos acuerdan quién lidera
- Tolerancia a fallos: Funciona con 2/3 nodos vivos

**Flujo de failover**:
```
1. Nodo 1 (Primary) cae
2. etcd detecta (heartbeat falla)
3. Patroni elige Nodo 2 como nuevo Primary
4. Clientes se reconectan a Nodo 2
5. Tiempo total: 10-30 segundos
```

---

## PARTE 3: Conceptos de Negocio

### 3.1 ¿Qué es Product-Market Fit?

**Definición**: Tu producto resuelve un problema real que la gente paga por resolver.

**Señales de PMF**:
- Clientes te buscan (no al revés)
- Churn <3%
- NPS >50
- Crecimiento orgánico (word of mouth)

**Cómo validar**:
1. **Pilotos**: 3 empresas usan gratis 30 días
2. **Feedback**: "No puedo vivir sin esto"
3. **Conversión**: 80%+ de pilotos pagan

**Tu caso**: Necesitas 3 pilotos exitosos para demostrar PMF.

### 3.2 ¿Qué es Go-to-Market (GTM)?

**Definición**: Estrategia para llevar tu producto al mercado.

**Componentes**:
1. **Target**: ¿A quién vendes? (Startups 50-200 empleados)
2. **Channels**: ¿Cómo llegas? (LinkedIn, eventos, partners)
3. **Messaging**: ¿Qué dices? ("90% savings vs Datadog")
4. **Sales**: ¿Cómo vendes? (Self-service vs enterprise sales)

**Tu GTM (recomendado)**:
```
Fase 1: Product-Led Growth (self-service)
  → Landing page + free trial
  → Conversión automática

Fase 2: Sales-Led (enterprise)
  → Sales engineers
  → Custom deals
```

### 3.3 ¿Qué es SaaS vs Self-Hosted?

**SaaS (Software as a Service)**:
- Ejemplo: Datadog, Gmail
- Tú manejas servidores
- Cliente paga mensual
- Fácil de escalar

**Self-Hosted**:
- Ejemplo: Sentinel, GitLab
- Cliente maneja servidores
- Cliente paga licencia
- Más control/privacy

**Hybrid (tu modelo ideal)**:
```
Opción A: Self-hosted (DIY)
  → $5-10/host/month
  → Cliente instala

Opción B: Managed (SaaS)
  → $15-20/host/month
  → Tú instalas y manejas
```

### 3.4 ¿Qué es Competitive Moat?

**Definición**: Ventaja competitiva difícil de copiar.

**Tipos**:
1. **Network effects**: Más usuarios = más valor (ej: Facebook)
2. **Switching costs**: Difícil cambiar (ej: Salesforce)
3. **Technology**: Patentes, know-how único
4. **Brand**: Marca fuerte (ej: Apple)

**Tu moat (Sentinel)**:
1. **Technology**: AI local + HA nativa (difícil de replicar)
2. **Switching costs**: Una vez instalado, difícil migrar
3. **Data privacy**: Compliance built-in (ventaja regulatoria)

---

## PARTE 4: Métricas que Debes Dominar

### 4.1 Unit Economics

**Pregunta**: ¿Ganas dinero por cada cliente?

**Cálculo**:
```
Revenue per customer: $800/mes x 36 meses = $28,800
Cost per customer:
  - CAC: $5,000
  - COGS: $50/mes x 36 = $1,800
  - Support: $100/mes x 36 = $3,600
Total cost: $10,400

Profit per customer: $28,800 - $10,400 = $18,400 ✅
```

**Ratio**: $18,400 / $10,400 = 1.77 (bueno, >1.5)

### 4.2 Burn Rate

**Definición**: Cuánto dinero gastas por mes.

**Cálculo**:
```
Salarios: $33K/mes (3 ingenieros)
Ops: $5K/mes (servidores, tools)
Marketing: $10K/mes
Total: $48K/mes burn rate
```

**Runway**: Cuánto tiempo tienes antes de quedarte sin dinero.

```
Runway = Cash / Burn rate
Ejemplo: $2M / $48K = 41 meses ✅
```

**Regla**: Siempre tener 12-18 meses de runway.

### 4.3 Growth Rate

**Definición**: Qué tan rápido creces.

**Cálculo**:
```
MoM (Month-over-Month):
Mes 1: $10K MRR
Mes 2: $12K MRR
Growth: ($12K - $10K) / $10K = 20% MoM
```

**Benchmark SaaS**:
- Excelente: >20% MoM
- Bueno: 10-20% MoM
- Malo: <10% MoM

**Proyección**:
```
Mes 1: $10K
Mes 12: $10K x (1.20)^11 = $74K MRR = $888K ARR
```

---

## PARTE 5: Conversaciones con Inversores

### 5.1 Preguntas Típicas (y Cómo Responder)

**P: ¿Por qué no Datadog?**
R: "Datadog es excelente para cloud-native, pero cuesta $180K/año para 100 hosts. Sentinel ofrece 90% de las features a $10K/año, ideal para mid-market que no puede pagar Datadog."

**P: ¿Cómo compites con Grafana (gratis)?**
R: "Grafana es solo dashboards, no tiene AI, no tiene HA nativa, requiere 5+ tools para replicar Sentinel. Nosotros somos all-in-one."

**P: ¿Cuál es tu moat?**
R: "AI local (privacy-first) + HA nativa. Competidores cobran extra por HA, nosotros lo incluimos. Además, compliance built-in (GDPR/CCPA)."

**P: ¿Cuántos clientes tienes?**
R: "3 pilotos activos, 2 convertidos a pago. MRR: $1.6K. Pipeline: 10 empresas interesadas."

**P: ¿Cuál es tu CAC?**
R: "Actualmente $0 (product-led growth). Proyectamos $5K con sales team. LTV: $28.8K. Ratio: 5.76x."

**P: ¿Qué haces con $2M?**
R: "Contratar 3 ingenieros ($400K), marketing ($200K), ops ($100K). Runway: 18 meses. Objetivo: $500K ARR, 50 clientes."

### 5.2 Red Flags (Qué NO Decir)

❌ "No tenemos competencia" (mentira, siempre hay)
✅ "Competimos con Datadog, pero en precio y privacy"

❌ "Vamos a ser el próximo unicornio" (arrogante)
✅ "Apuntamos a $10M ARR en 5 años"

❌ "La tecnología se vende sola" (naive)
✅ "Tenemos estrategia GTM clara: product-led + sales"

❌ "Necesitamos el dinero ya" (desesperado)
✅ "Levantamos para acelerar, no para sobrevivir"

### 5.3 Términos de Negociación

**Valuation**: ¿Cuánto vale tu empresa?
- Pre-money: Antes de la inversión
- Post-money: Después de la inversión

**Ejemplo**:
```
Pre-money: $10M
Inversión: $2M
Post-money: $12M
Equity vendido: $2M / $12M = 16.67%
```

**Liquidation Preference**: Quién cobra primero si vendes.
- 1x: Inversor recupera su dinero primero
- 2x: Inversor recupera 2x su dinero primero

**Vesting**: Cuándo recibes tu equity.
- Típico: 4 años, 1 año cliff
- Significa: 25% por año, nada el primer año

---

## PARTE 6: Checklist Pre-Reunión con Inversor

### Antes de la Reunión

- [ ] Pitch deck actualizado (10 slides)
- [ ] Demo funcionando (sin bugs)
- [ ] Financials listos (3 años proyección)
- [ ] Investigar al VC (portfolio, tesis)
- [ ] Preparar 3 preguntas para ellos

### Durante la Reunión

- [ ] Llegar 5 min antes
- [ ] Laptop cargado + backup (USB)
- [ ] Contar historia (no leer slides)
- [ ] Escuchar feedback
- [ ] Tomar notas

### Después de la Reunión

- [ ] Email de seguimiento (24 horas)
- [ ] Enviar materiales solicitados
- [ ] Conectar en LinkedIn
- [ ] Agendar próxima reunión

---

## PARTE 7: Recursos y Herramientas

### Para Crear Pitch Deck
- **Canva**: Templates gratis
- **Pitch**: Colaborativo
- **Google Slides**: Simple y efectivo

### Para Financial Model
- **Google Sheets**: Template SaaS
- **Causal**: Modeling tool
- **Excel**: Clásico

### Para Encontrar Inversores
- **Crunchbase**: Base de datos VCs
- **AngelList**: Plataforma de inversión
- **LinkedIn**: Networking

### Para Aprender Más
- **Y Combinator**: Startup School (gratis)
- **a16z Podcast**: Insights de VCs
- **SaaStr**: Comunidad SaaS

---

## Conclusión

Jaime, ahora tienes TODO lo que necesitas para:
1. ✅ Entender cada concepto
2. ✅ Hablar con inversores con confianza
3. ✅ Responder cualquier pregunta
4. ✅ Negociar términos

**Próximo paso**: Crear tu pitch deck con estos conceptos.

**Recuerda**: Los inversores invierten en **personas**, no en ideas. Muestra pasión, conocimiento y capacidad de ejecución.

¡Estás listo! 
