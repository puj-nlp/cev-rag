# 🕊 Cultural Context-Aware Question-Answering System for the Colombian Truth Commission

### Proyecto financiado por el Notre Dame–IBM Technology Ethics Lab  
**Convocatoria:** 2024 CFP: The Ethics of Large-Scale Models  
**Monto asignado:** USD $60,000  
**Período:** Hasta julio de 2025  

---

## Objetivo

Desarrollar un sistema RAG (Retrieval-Augmented Generation) sensible al contexto cultural para explorar el archivo de la Comisión de la Verdad de Colombia. Este archivo digital, pionero en procesos de paz, contiene una vasta cantidad de documentos que hacen inviable el análisis manual.

El sistema permite hacer preguntas naturales y obtener respuestas precisas con base en evidencia documental, mejorando la accesibilidad, la comprensión y el uso del archivo por parte de investigadores, instituciones y la sociedad civil.

---

## Equipos del Proyecto

### Equipo de Investigación Principal  
Responsables de orientar toda la estructura y ejecución del proyecto.  
- **PhD Luis Gabriel Moreno Sandoval** – Pontificia Universidad Javeriana  
  📧 morenoluis@javeriana.edu.co  
- **PhD Matthew Sisk** – Lucy Family Institute for Data & Society (University of Notre Dame)  
  📧 msisk1@nd.edu  
- **Anna Sokol** – Estudiante de doctorado, Lucy Family Institute for Data & Society  
  📧 asokol@nd.edu  
- **Maria Prada Ramírez** – Fellow, Kroc Institute for International Peace Studies  
  📧 mpradara@nd.edu  

---

### Equipo de Ética y Validación Técnica  

Responsables de evaluar la sensibilidad de la herramienta ante temáticas de memoria, conflicto, derechos humanos y diversidad cultural. Este equipo colaboró en el diseño de los ejercicios de validación junto con personas expertas en justicia transicional y el archivo de la Comisión de la Verdad.

**Integrantes:**  
- **Leonardo Andrés Ibañez Tirado**  
  Exmiembro de la Comisión de la Verdad  
  📧 leo23_ml@outlook.com  

- **Viviana Gómez León**  
  Estudiante de Ingeniería de Sistemas, Pontificia Universidad Javeriana  
  📧 gomezlv@javeriana.edu.co  

- **Juan Felipe Rubiano Santacruz**  
  Estudiante de Ingeniería de Sistemas, Pontificia Universidad Javeriana  
  📧 rubiano_jf@javeriana.edu.co  

- **Juan Pablo Arias Buitrago**  
  Estudiante de Ciencia de Datos, Pontificia Universidad Javeriana  
  📧 ariasj.u@javeriana.edu.co  

---

### Equipo Técnico de Desarrollo y Despliegue

Encargados de la implementación de la arquitectura, desarrollo y despliegue de la herramienta RAG en infraestructura web, incluyendo APIs, contenedores Docker y la interfaz interactiva.

**Integrantes:**  
- **Daniel Steven Moreno Sandoval**  
  Estudiante de Maestría en Inteligencia Artificial, Universidad de los Andes  
  📧 ds.morenos1@uniandes.edu.co  

- **PhD Luis Gabriel Moreno Sandoval**  
  Investigador principal y líder de despliegue técnico  
  📧 morenoluis@javeriana.edu.co  

---

## Estructura del Proyecto

```plaintext
cev-rag/
│
├── milvus_db/                     # Base de datos vectorial Milvus
├── notebook/                      # Notebooks exploratorios
├── rag-api/                       # Backend con FastAPI
├── rag-ui/                        # Interfaz web
├── .env.example                   # Variables de entorno
├── docker-compose.yml            # Despliegue estándar
├── LICENSE
└── README.md
```

---

## ¿Cómo ejecutar?

```bash
git clone https://github.com/puj-nlp/cev-rag.git
cd cev-rag
cp .env.example .env
docker-compose up --build
```

- API disponible en `http://localhost:8000`  
- Interfaz web en `http://localhost:3000` o vía Nginx

---

## Documentación y Ética

- [ReporteTécnico de la Revisión Ética (es) (PDF)](./docs/reporte_es.pdf)
- [Ethics Review Technical Report (en) (PDF)](./docs/reporte_en.pdf)

[//]: # ([Preprint de Articulo &#40;PDF&#41;]&#40;./docs/Tech_Ethics_CFP_2025_Program.pdf&#41;)

> Este trabajo está basado en fondos otorgados por el Notre Dame–IBM Tech Ethics Lab. Dicho apoyo no constituye una aprobación de los puntos de vista expresados en esta publicación.

---

## Eventos Asociados

#### Tech Ethics Forum 2025 – University of Notre Dame

**Nombre del evento:** *Tech Ethics Forum: The Ethics of Large-Scale Models*  
**Fecha:** 22 y 23 de enero de 2025  
**Lugar:** Universidad de Notre Dame, McKenna Hall  

Este foro académico internacional reunió a investigadores de todo el mundo para presentar los resultados de los proyectos financiados por el Notre Dame–IBM Tech Ethics Lab en su convocatoria 2024.  
El Dr. **Luis Gabriel Moreno Sandoval** participó como ponente invitado en el panel **"Memory, History, and AI"**, donde se discutió cómo los sistemas de inteligencia artificial impactan la preservación, interpretación y uso de la memoria histórica, especialmente en contextos de conflicto armado.

El evento contó con la presencia de expertos en ética, tecnología, filosofía y derechos humanos, y se destacó como un espacio de discusión crítica sobre el uso responsable de modelos de lenguaje a gran escala.

---

#### Evento de Socialización Pública – Pontificia Universidad Javeriana

**Nombre del evento:** *Presentación pública de la herramienta “Ventana de la Verdad”*  
**Fecha:** Diciembre de 2024  
**Lugar:** Facultad de Ingeniería, Pontificia Universidad Javeriana, Bogotá  

Este evento tuvo como propósito presentar públicamente los resultados del proyecto ante comunidades clave en Colombia. Se contó con la participación de representantes de la **Jurisdicción Especial para la Paz (JEP)**, la **Comisión de la Verdad**, organizaciones de **víctimas del conflicto armado**, y **organizaciones de la sociedad civil**.

Durante el evento se realizaron demostraciones en vivo de la herramienta, se presentaron sus aportes para la accesibilidad al archivo de la Comisión de la Verdad, y se abrió un espacio de diálogo con los asistentes sobre el rol de la inteligencia artificial en los procesos de memoria, verdad y justicia.

---

## Licencia

Distribuido bajo licencia [MIT](./LICENSE).  
Los entregables se publicarán bajo licencia de acceso abierto y/o código abierto, de acuerdo con los lineamientos del Notre Dame–IBM Tech Ethics Lab.

---

## Contacto

**Autor y Mantenimiento:**  
PhD Luis Gabriel Moreno Sandoval  
Pontificia Universidad Javeriana  
📧 morenoluis@javeriana.edu.co
