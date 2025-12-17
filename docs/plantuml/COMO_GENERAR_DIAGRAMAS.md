# 🎨 CÓMO GENERAR LOS DIAGRAMAS UML
**Sentinel Cortex™ - Instrucciones para Generar PNG/SVG**

**Fecha:** 17 Diciembre 2025  
**Archivos:** diagram1_vagus_nerve.puml, diagram2_dual_guardian.puml

---

## ✅ ARCHIVOS LISTOS

Los archivos PlantUML están en:
```
/home/jnovoas/sentinel/docs/plantuml/diagram1_vagus_nerve.puml
/home/jnovoas/sentinel/docs/plantuml/diagram2_dual_guardian.puml
```

---

## 🌐 OPCIÓN 1: PLANTUML ONLINE (MÁS RÁPIDO - RECOMENDADO)

### Paso 1: Ir al Editor Online
Abrir: https://www.plantuml.com/plantuml/uml/

### Paso 2: Generar Diagrama 1 (Vagus Nerve)
1. Abrir archivo: `/home/jnovoas/sentinel/docs/plantuml/diagram1_vagus_nerve.puml`
2. Copiar TODO el contenido
3. Pegar en el editor online
4. Click "Submit"
5. Click derecho en la imagen → "Save image as..."
6. Guardar como: `diagram1_vagus_nerve.png`

### Paso 3: Generar Diagrama 2 (Dual-Guardian)
1. Abrir archivo: `/home/jnovoas/sentinel/docs/plantuml/diagram2_dual_guardian.puml`
2. Copiar TODO el contenido
3. Pegar en el editor online
4. Click "Submit"
5. Click derecho en la imagen → "Save image as..."
6. Guardar como: `diagram2_dual_guardian.png`

### Paso 4: Mover Imágenes
```bash
mv ~/Downloads/diagram1_vagus_nerve.png /home/jnovoas/sentinel/docs/plantuml/
mv ~/Downloads/diagram2_dual_guardian.png /home/jnovoas/sentinel/docs/plantuml/
```

---

## 💻 OPCIÓN 2: INSTALAR PLANTUML LOCALMENTE

### Instalar Java (Requerido)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install default-jre

# Verificar instalación
java -version
```

### Descargar PlantUML
```bash
cd /tmp
wget https://github.com/plantuml/plantuml/releases/download/v1.2024.3/plantuml-1.2024.3.jar
```

### Generar Diagramas
```bash
cd /home/jnovoas/sentinel/docs/plantuml

# Generar ambos diagramas
java -jar /tmp/plantuml-1.2024.3.jar diagram1_vagus_nerve.puml diagram2_dual_guardian.puml

# Output:
# - diagram1_vagus_nerve.png
# - diagram2_dual_guardian.png
```

### Generar SVG (Opcional - Mejor Calidad)
```bash
java -jar /tmp/plantuml-1.2024.3.jar -tsvg diagram1_vagus_nerve.puml diagram2_dual_guardian.puml

# Output:
# - diagram1_vagus_nerve.svg
# - diagram2_dual_guardian.svg
```

---

## 🔧 OPCIÓN 3: VS CODE EXTENSION

### Instalar Extensión
1. Abrir VS Code
2. Ir a Extensions (Ctrl+Shift+X)
3. Buscar "PlantUML"
4. Instalar "PlantUML" by jebbs

### Generar Diagramas
1. Abrir `diagram1_vagus_nerve.puml` en VS Code
2. Presionar `Alt+D` para preview
3. Click derecho en preview → "Export Current Diagram"
4. Seleccionar formato: PNG o SVG
5. Guardar en `/home/jnovoas/sentinel/docs/plantuml/`

6. Repetir para `diagram2_dual_guardian.puml`

---

## 📋 VERIFICAR RESULTADOS

### Archivos Generados Esperados:
```
/home/jnovoas/sentinel/docs/plantuml/
├── diagram1_vagus_nerve.puml      (✅ Ya existe)
├── diagram1_vagus_nerve.png       (⏰ Pendiente generar)
├── diagram2_dual_guardian.puml    (✅ Ya existe)
└── diagram2_dual_guardian.png     (⏰ Pendiente generar)
```

### Verificar Calidad:
- **Resolución mínima:** 1920x1080 (para presentaciones)
- **Formato preferido:** PNG (para patent filing)
- **Formato alternativo:** SVG (para edición posterior)

---

## 📧 PARA PATENT ATTORNEY

### Una Vez Generados los PNG:

1. **Incluir en email:**
   ```
   Adjuntos:
   - diagram1_vagus_nerve.png (Figure 1: The Vagus Nerve)
   - diagram2_dual_guardian.png (Figure 2: Dual-Guardian Architecture)
   ```

2. **Referencias en documentación:**
   - MASTER_SECURITY_IP_CONSOLIDATION.md: "Ver Figura 1..." y "Ver Figura 2..."
   - PATENT_ADDITIONAL_BLOCKS.md: Incluir imágenes inline

3. **Para provisional patent:**
   - Figure 1: Cognitive Syscall Interception (The Vagus Nerve)
   - Figure 2: Dual-Guardian Mutual Surveillance Architecture

---

## ✅ CHECKLIST

- [ ] Generar diagram1_vagus_nerve.png
- [ ] Generar diagram2_dual_guardian.png
- [ ] Verificar calidad (legible, alta resolución)
- [ ] Mover a /home/jnovoas/sentinel/docs/plantuml/
- [ ] Incluir en email a patent attorney
- [ ] Referenciar en MASTER_SECURITY_IP_CONSOLIDATION.md

---

## 🎯 PRÓXIMOS PASOS

1. **HOY:** Generar PNG usando Opción 1 (online - 5 minutos)
2. **MAÑANA:** Enviar a patent attorney junto con documentación
3. **ESTA SEMANA:** Incluir en provisional patent draft

---

**Documento:** Instrucciones para Generar Diagramas UML  
**Status:** ✅ ARCHIVOS .PUML LISTOS  
**Pendiente:** Generar PNG (5 minutos con opción online)  
**Recomendación:** Usar Opción 1 (PlantUML Online) - más rápido
