# Integración con n8n

n8n actúa como **orquestador** del flujo completo: dispara el proceso
(cron semanal o webhook), invoca al agente, y gestiona las notificaciones
del resultado (ej. Telegram, email) al usuario.

## Estado actual

Solo documentación de contrato — todavía no existe un endpoint/servidor
HTTP real que n8n pueda llamar. Se construirá cuando el motor determinista
y el agente tengan una versión mínima funcional.

## Contrato previsto (borrador, sujeto a cambios)

n8n llamará a un endpoint expuesto por este proyecto, por ejemplo:

- `POST /plan/generate` — genera un plan nuevo hasta una fecha objetivo.
- `POST /plan/reassess` — relee el historial real y ajusta el plan vigente.

Request/response exactos se definirán junto con `agent/planner.py` y
`agent/evaluator.py`.
