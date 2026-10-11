#  Psychology-to-n8n Pipeline
## *Automated Extraction of Behavioral Patterns → n8n Workflows*

**Fecha**: 2025-12-17  
**Propósito**: Convertir conocimiento de psicología/psiquiatría en workflows ejecutables

---

##  El Concepto

### **Pipeline Completo**:

```
LIBROS/PAPERS PSICOLOGÍA
    ↓
[1] PDF/Text Extraction
    ↓
[2] NLP Pattern Recognition (GPT-4)
    ↓
[3] Behavioral Pattern Database
    ↓
[4] n8n Workflow Generator
    ↓
[5] Truth Algorithm Integration
```

---

## 📚 Fuentes de Conocimiento

### **Libros Clave de Psicología del Engaño**:

1. **"Telling Lies" - Paul Ekman**
   - Microexpresiones faciales
   - Señales de engaño verbal
   - Gestos inconscientes

2. **"The Psychology of Lying" - Bella DePaulo**
   - Patrones lingüísticos de mentira
   - Contexto social del engaño
   - Diferencias culturales

3. **"Spy the Lie" - Philip Houston (ex-CIA)**
   - Técnicas de interrogatorio
   - Señales de estrés
   - Timing de respuestas

4. **Papers Académicos**:
   - Journal of Nonverbal Behavior
   - Psychological Science
   - Emotion (APA)

---

## 🔧 Implementación: Python Pipeline

### **Paso 1: Extracción de Texto**

```python
# psychology_to_n8n/extract_text.py
import PyPDF2
import re
from pathlib import Path

class PsychologyBookExtractor:
    def __init__(self, book_path: str):
        self.book_path = Path(book_path)
        self.text = ""
        
    def extract_pdf(self) -> str:
        """Extrae texto de PDF"""
        with open(self.book_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                self.text += page.extract_text()
        return self.text
    
    def extract_chapters(self) -> dict:
        """Divide en capítulos"""
        chapters = {}
        current_chapter = None
        
        for line in self.text.split('\n'):
            # Detecta capítulos (ej: "Chapter 3: Microexpressions")
            if re.match(r'^Chapter \d+:', line):
                current_chapter = line
                chapters[current_chapter] = []
            elif current_chapter:
                chapters[current_chapter].append(line)
        
        return chapters

# Uso
extractor = PsychologyBookExtractor("books/telling_lies_ekman.pdf")
chapters = extractor.extract_chapters()
```

---

### **Paso 2: Pattern Recognition con GPT-4**

```python
# psychology_to_n8n/pattern_recognition.py
import openai
from typing import List, Dict
import json

class BehavioralPatternExtractor:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
    def extract_patterns(self, chapter_text: str) -> List[Dict]:
        """Extrae patrones comportamentales usando GPT-4"""
        
        prompt = f"""
        Analiza el siguiente texto de psicología del engaño y extrae patrones comportamentales específicos.
        
        Para cada patrón, proporciona:
        1. Nombre del patrón
        2. Descripción técnica
        3. Señales observables (qué buscar)
        4. Timing (cuándo ocurre)
        5. Confidence score (qué tan confiable es)
        6. Categoría (facial, vocal, gestual, lingüístico, temporal)
        
        Formato JSON:
        {{
            "patterns": [
                {{
                    "name": "Microexpresión de Miedo",
                    "description": "Expresión facial involuntaria que dura <200ms",
                    "signals": ["cejas levantadas", "ojos abiertos", "boca tensa"],
                    "timing": "0.1-0.3s antes o después del claim",
                    "confidence": 0.85,
                    "category": "facial"
                }}
            ]
        }}
        
        Texto:
        {chapter_text}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "Eres un experto en psicología del engaño y análisis comportamental."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        patterns = json.loads(response.choices[0].message.content)
        return patterns['patterns']

# Uso
extractor = BehavioralPatternExtractor(api_key="sk-...")
patterns = extractor.extract_patterns(chapters["Chapter 3: Microexpressions"])

# Output ejemplo:
# [
#   {
#     "name": "Microexpresión de Desprecio",
#     "description": "Labio superior levantado unilateralmente",
#     "signals": ["labio superior izquierdo/derecho levantado", "asimetría facial"],
#     "timing": "durante o inmediatamente después del claim",
#     "confidence": 0.82,
#     "category": "facial"
#   }
# ]
```

---

### **Paso 3: Behavioral Pattern Database**

```python
# psychology_to_n8n/pattern_database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class BehavioralPattern(Base):
    __tablename__ = 'behavioral_patterns'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    signals = Column(JSON)  # Lista de señales observables
    timing = Column(String)
    confidence = Column(Float)
    category = Column(String)  # facial, vocal, gestual, lingüístico, temporal
    source_book = Column(String)  # "Telling Lies - Ekman"
    source_page = Column(Integer)
    
class PatternDatabase:
    def __init__(self, db_url: str = "sqlite:///patterns.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_pattern(self, pattern: dict, source_book: str, source_page: int):
        """Agrega patrón a la base de datos"""
        db_pattern = BehavioralPattern(
            name=pattern['name'],
            description=pattern['description'],
            signals=pattern['signals'],
            timing=pattern['timing'],
            confidence=pattern['confidence'],
            category=pattern['category'],
            source_book=source_book,
            source_page=source_page
        )
        self.session.add(db_pattern)
        self.session.commit()
    
    def get_patterns_by_category(self, category: str) -> list:
        """Obtiene patrones por categoría"""
        return self.session.query(BehavioralPattern).filter_by(category=category).all()
    
    def get_all_patterns(self) -> list:
        """Obtiene todos los patrones"""
        return self.session.query(BehavioralPattern).all()

# Uso
db = PatternDatabase()
for pattern in patterns:
    db.add_pattern(pattern, source_book="Telling Lies - Ekman", source_page=47)
```

---

### **Paso 4: n8n Workflow Generator**

```python
# psychology_to_n8n/workflow_generator.py
import json
from typing import Dict, List

class N8nWorkflowGenerator:
    def __init__(self):
        self.workflow_template = {
            "name": "",
            "nodes": [],
            "connections": {},
            "active": True,
            "settings": {}
        }
    
    def generate_workflow(self, pattern: Dict) -> Dict:
        """Genera workflow n8n desde patrón comportamental"""
        
        workflow = self.workflow_template.copy()
        workflow['name'] = f"Truth Detection - {pattern['name']}"
        
        # Nodo 1: Webhook trigger
        webhook_node = {
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "position": [240, 300],
            "parameters": {
                "path": f"truth/{pattern['category']}/{pattern['name'].lower().replace(' ', '_')}",
                "httpMethod": "POST"
            }
        }
        
        # Nodo 2: Pattern detection (específico por categoría)
        if pattern['category'] == 'facial':
            detection_node = self._generate_facial_detection_node(pattern)
        elif pattern['category'] == 'vocal':
            detection_node = self._generate_vocal_detection_node(pattern)
        elif pattern['category'] == 'lingüístico':
            detection_node = self._generate_linguistic_detection_node(pattern)
        else:
            detection_node = self._generate_generic_detection_node(pattern)
        
        # Nodo 3: Scoring
        scoring_node = {
            "name": "Calculate Deception Score",
            "type": "n8n-nodes-base.function",
            "position": [900, 300],
            "parameters": {
                "functionCode": self._generate_scoring_function(pattern)
            }
        }
        
        # Nodo 4: Output
        output_node = {
            "name": "Truth Guardian Output",
            "type": "n8n-nodes-base.respondToWebhook",
            "position": [1120, 300],
            "parameters": {
                "respondWith": "json"
            }
        }
        
        workflow['nodes'] = [webhook_node, detection_node, scoring_node, output_node]
        
        # Conexiones
        workflow['connections'] = {
            "Webhook": {"main": [[{"node": detection_node['name'], "type": "main", "index": 0}]]},
            detection_node['name']: {"main": [[{"node": "Calculate Deception Score", "type": "main", "index": 0}]]},
            "Calculate Deception Score": {"main": [[{"node": "Truth Guardian Output", "type": "main", "index": 0}]]}
        }
        
        return workflow
    
    def _generate_facial_detection_node(self, pattern: Dict) -> Dict:
        """Genera nodo de detección facial"""
        return {
            "name": "Facial Pattern Detection",
            "type": "n8n-nodes-base.httpRequest",
            "position": [680, 300],
            "parameters": {
                "url": "https://api.openai.com/v1/chat/completions",
                "method": "POST",
                "headers": {"Authorization": "Bearer {{ $env.OPENAI_KEY }}"},
                "body": {
                    "model": "gpt-4-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Detecta el siguiente patrón: {pattern['description']}. Señales: {', '.join(pattern['signals'])}"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": "{{ $json.image_url }}"}
                                }
                            ]
                        }
                    ]
                }
            }
        }
    
    def _generate_vocal_detection_node(self, pattern: Dict) -> Dict:
        """Genera nodo de detección vocal"""
        return {
            "name": "Vocal Pattern Detection",
            "type": "n8n-nodes-base.function",
            "position": [680, 300],
            "parameters": {
                "functionCode": f"""
                const audio = items[0].json.audio;
                const transcript = items[0].json.transcript;
                
                // Detectar: {pattern['description']}
                // Señales: {', '.join(pattern['signals'])}
                
                let score = 0;
                {self._generate_signal_detection_code(pattern['signals'])}
                
                return [{{json: {{pattern_detected: score > 0.5, score, signals: {pattern['signals']}}}}}];
                """
            }
        }
    
    def _generate_linguistic_detection_node(self, pattern: Dict) -> Dict:
        """Genera nodo de detección lingüística"""
        return {
            "name": "Linguistic Pattern Detection",
            "type": "n8n-nodes-base.function",
            "position": [680, 300],
            "parameters": {
                "functionCode": f"""
                const text = items[0].json.transcript;
                
                // Detectar: {pattern['description']}
                // Señales: {', '.join(pattern['signals'])}
                
                let score = 0;
                {self._generate_text_pattern_code(pattern['signals'])}
                
                return [{{json: {{pattern_detected: score > 0.5, score}}}}];
                """
            }
        }
    
    def _generate_scoring_function(self, pattern: Dict) -> str:
        """Genera función de scoring basada en confidence del patrón"""
        return f"""
        const detected = items[0].json.pattern_detected;
        const base_confidence = {pattern['confidence']};
        
        const deception_score = detected ? base_confidence : 0;
        
        return [{{
            json: {{
                pattern_name: "{pattern['name']}",
                deception_score,
                confidence: base_confidence,
                category: "{pattern['category']}",
                detected
            }}
        }}];
        """
    
    def _generate_signal_detection_code(self, signals: List[str]) -> str:
        """Genera código para detectar señales vocales"""
        code = ""
        for signal in signals:
            code += f"""
            if (transcript.includes("{signal}")) score += 0.{len(signals)};
            """
        return code
    
    def _generate_text_pattern_code(self, signals: List[str]) -> str:
        """Genera código para detectar patrones de texto"""
        code = ""
        for signal in signals:
            code += f"""
            const {signal.replace(' ', '_')}_count = (text.match(/{signal}/gi) || []).length;
            if ({signal.replace(' ', '_')}_count > 0) score += 0.{len(signals)};
            """
        return code
    
    def save_workflow(self, workflow: Dict, filename: str):
        """Guarda workflow en archivo JSON"""
        with open(filename, 'w') as f:
            json.dump(workflow, f, indent=2)

# Uso
generator = N8nWorkflowGenerator()

# Para cada patrón en la base de datos
db = PatternDatabase()
patterns = db.get_all_patterns()

for pattern in patterns:
    pattern_dict = {
        'name': pattern.name,
        'description': pattern.description,
        'signals': pattern.signals,
        'timing': pattern.timing,
        'confidence': pattern.confidence,
        'category': pattern.category
    }
    
    workflow = generator.generate_workflow(pattern_dict)
    generator.save_workflow(workflow, f"n8n_workflows/{pattern.name.replace(' ', '_')}.json")
```

---

##  Pipeline Completo Automatizado

```python
# psychology_to_n8n/main.py
import os
from pathlib import Path
from extract_text import PsychologyBookExtractor
from pattern_recognition import BehavioralPatternExtractor
from pattern_database import PatternDatabase
from workflow_generator import N8nWorkflowGenerator

class PsychologyToN8nPipeline:
    def __init__(self, openai_api_key: str):
        self.text_extractor = None
        self.pattern_extractor = BehavioralPatternExtractor(openai_api_key)
        self.db = PatternDatabase()
        self.workflow_generator = N8nWorkflowGenerator()
    
    def process_book(self, book_path: str, book_name: str):
        """Procesa un libro completo"""
        print(f"📚 Procesando: {book_name}")
        
        # 1. Extraer texto
        print("  [1/5] Extrayendo texto...")
        self.text_extractor = PsychologyBookExtractor(book_path)
        chapters = self.text_extractor.extract_chapters()
        
        # 2. Extraer patrones de cada capítulo
        print(f"  [2/5] Extrayendo patrones de {len(chapters)} capítulos...")
        all_patterns = []
        for chapter_name, chapter_text in chapters.items():
            chapter_text_str = '\n'.join(chapter_text)
            patterns = self.pattern_extractor.extract_patterns(chapter_text_str)
            all_patterns.extend(patterns)
            print(f"    ✓ {chapter_name}: {len(patterns)} patrones")
        
        # 3. Guardar en base de datos
        print(f"  [3/5] Guardando {len(all_patterns)} patrones en DB...")
        for pattern in all_patterns:
            self.db.add_pattern(pattern, source_book=book_name, source_page=0)
        
        # 4. Generar workflows n8n
        print("  [4/5] Generando workflows n8n...")
        os.makedirs("n8n_workflows", exist_ok=True)
        for pattern in all_patterns:
            workflow = self.workflow_generator.generate_workflow(pattern)
            filename = f"n8n_workflows/{pattern['name'].replace(' ', '_')}.json"
            self.workflow_generator.save_workflow(workflow, filename)
            print(f"    ✓ {filename}")
        
        # 5. Generar resumen
        print("  [5/5] Generando resumen...")
        self.generate_summary(all_patterns, book_name)
        
        print(f"✅ Completado: {len(all_patterns)} patrones → {len(all_patterns)} workflows")
    
    def generate_summary(self, patterns: list, book_name: str):
        """Genera resumen de patrones extraídos"""
        summary = f"# Patrones Extraídos: {book_name}\n\n"
        summary += f"**Total**: {len(patterns)} patrones\n\n"
        
        # Por categoría
        categories = {}
        for pattern in patterns:
            cat = pattern['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(pattern)
        
        for category, cat_patterns in categories.items():
            summary += f"## {category.capitalize()} ({len(cat_patterns)} patrones)\n\n"
            for pattern in cat_patterns:
                summary += f"### {pattern['name']}\n"
                summary += f"- **Descripción**: {pattern['description']}\n"
                summary += f"- **Señales**: {', '.join(pattern['signals'])}\n"
                summary += f"- **Timing**: {pattern['timing']}\n"
                summary += f"- **Confidence**: {pattern['confidence']}\n\n"
        
        with open(f"summaries/{book_name.replace(' ', '_')}_summary.md", 'w') as f:
            f.write(summary)

# Uso
if __name__ == "__main__":
    pipeline = PsychologyToN8nPipeline(openai_api_key="sk-...")
    
    # Procesar libros
    books = [
        ("books/telling_lies_ekman.pdf", "Telling Lies - Ekman"),
        ("books/psychology_of_lying_depaulo.pdf", "Psychology of Lying - DePaulo"),
        ("books/spy_the_lie_houston.pdf", "Spy the Lie - Houston")
    ]
    
    for book_path, book_name in books:
        pipeline.process_book(book_path, book_name)
    
    # Estadísticas finales
    db = PatternDatabase()
    total_patterns = len(db.get_all_patterns())
    print(f"\n Total de patrones en DB: {total_patterns}")
    print(f" Total de workflows generados: {total_patterns}")
```

---

## 📊 Output Esperado

### **De 3 libros**:
- **Telling Lies (Ekman)**: ~50 patrones
- **Psychology of Lying (DePaulo)**: ~30 patrones
- **Spy the Lie (Houston)**: ~40 patrones
- **Total**: ~120 patrones → 120 workflows n8n

### **Categorías**:
- Facial: 30 workflows
- Vocal: 25 workflows
- Gestual: 20 workflows
- Lingüístico: 30 workflows
- Temporal: 15 workflows

---

##  Integración con Truth Algorithm

```python
# Cargar workflows en n8n
import requests

class N8nIntegration:
    def __init__(self, n8n_url: str, api_key: str):
        self.n8n_url = n8n_url
        self.headers = {"X-N8N-API-KEY": api_key}
    
    def upload_workflow(self, workflow: dict):
        """Sube workflow a n8n"""
        response = requests.post(
            f"{self.n8n_url}/api/v1/workflows",
            json=workflow,
            headers=self.headers
        )
        return response.json()
    
    def upload_all_workflows(self, workflow_dir: str):
        """Sube todos los workflows"""
        for filename in Path(workflow_dir).glob("*.json"):
            with open(filename) as f:
                workflow = json.load(f)
            result = self.upload_workflow(workflow)
            print(f"✓ Uploaded: {workflow['name']}")

# Uso
n8n = N8nIntegration(n8n_url="http://localhost:5678", api_key="your-api-key")
n8n.upload_all_workflows("n8n_workflows")
```

---

## ✅ Ventajas

1. **Automatizado**: Procesa libros completos en minutos
2. **Escalable**: Agrega más libros fácilmente
3. **Científico**: Basado en literatura académica
4. **Trazable**: Cada patrón tiene fuente (libro + página)
5. **Actualizable**: Re-procesa cuando salen nuevos papers

---

##  Próximos Pasos

1. **Implementar pipeline** (2-3 días)
2. **Procesar 3-5 libros clave** (1 día)
3. **Generar ~100-150 workflows** (automático)
4. **Integrar con Truth Algorithm** (1 día)
5. **Testing con videos reales** (1 semana)

**¿Quieres que implemente el pipeline completo?** 
