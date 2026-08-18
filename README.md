# PB_coach

Sistema que lee el historial real de entrenamiento de un atleta, genera un
plan hasta una fecha objetivo respetando reglas de metodología explícitas,
ajusta ese plan cuando la realidad se desvía, y justifica cada decisión
citando la regla que la produjo.

Prioriza un solo deporte por mesociclo. Nunca inventa metodología: la
aplica. Si no puede cumplir las restricciones, lo dice en vez de producir
un plan bonito e incoherente.

Este proyecto es también un ejercicio de aprendizaje de agentes de IA,
n8n y MCP.

## Principio de diseño

El sistema es un motor híbrido:

- **Motor determinista (Python)**: calcula carga/volumen/intensidad,
  valida restricciones de la metodología activa, detecta desviación entre
  plan y realidad. Es la única autoridad sobre "¿esto cumple la
  metodología?". Se testea con unit tests.
- **Agente LLM**: interpreta el objetivo del usuario, propone la
  composición de la rutina y los ajustes, evalúa el progreso en lenguaje
  natural y redacta la justificación citando el ID de regla exacto que el
  motor determinista usó. Nunca decide por sí solo si algo es válido —
  propone dentro del espacio que el motor aprueba o rechaza.

## Flujo (visión)

```
n8n (orquestador: cron / webhook)
  │
  ▼
Agente (Python) ──consulta──▶ MCP externo (ej. Strava) ──▶ historial real
  │
  ├──▶ Motor determinista (engine/) ◀── perfil de metodología activo (YAML)
  │        valida, calcula, detecta desviación
  │
  ├──▶ LLM (agent/) propone plan / ajuste / evaluación
  │        (solo dentro de lo que el engine aprueba)
  │
  ▼
Plan + justificación citando reglas ──▶ n8n notifica al usuario
```

## Estructura del proyecto

```
methodology/    Perfiles de metodología (YAML), uno por autor/framework
src/pb_coach/
  domain/       Modelos de datos puros (Sesión, Mesociclo, Plan, ...)
  engine/       Motor determinista: loader, calculator, validator, deviation
  agent/        Capa LLM: planner, evaluator, explainer
  mcp_client/   Cliente MCP para servidores externos (ej. Strava)
  integrations/n8n/  Contrato de los webhooks que n8n dispara
tests/          Tests, principalmente del motor determinista
docs/           Decisiones de arquitectura
```

## Estado actual

Fase de andamiaje inicial. Aún no hay lógica de negocio implementada.
Próximos pasos: definir `domain/`, transcribir un primer perfil de
metodología real y construir el motor determinista sobre fixtures de
prueba.

## Setup

```bash
pip install -e ".[dev]"
pytest
```
