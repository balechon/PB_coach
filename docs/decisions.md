# Decisiones de arquitectura

Registro breve (ADR-lite) de las decisiones tomadas y su motivo. Añadir una
entrada nueva cuando se tome una decisión de arquitectura relevante.

## 2026-08-18 — Motor híbrido: determinista + LLM

**Decisión**: el cálculo de carga/volumen/intensidad, la validación de
restricciones y la detección de desviación son deterministas (Python,
testeados). El LLM compone la rutina, evalúa progreso y redacta
justificaciones, pero siempre propone dentro del espacio que el motor
determinista valida — nunca es el árbitro de si algo cumple la metodología.

**Por qué**: el objetivo del proyecto exige que el sistema "nunca invente
metodología" y que "si no puede cumplir las restricciones, lo diga". Un LLM
puro puede alucinar reglas o forzar una solución "bonita" ante un conflicto
irresoluble. Separar el árbitro (determinista) del proponente (LLM) hace
que esa garantía sea verificable con tests, no solo una instrucción de
prompt.

## 2026-08-18 — Un perfil de metodología activo por plan

**Decisión**: cada plan usa un único perfil YAML (`methodology/profiles/`)
de un autor/framework. No se combinan reglas de distintos autores dentro
de un mismo plan.

**Por qué**: mezclar reglas de metodologías distintas puede generar
conflictos no resolubles sin criterio arbitrario. Mantener un perfil activo
por plan simplifica la validación y hace que cada regla citada sea
inequívocamente atribuible a una fuente.

## 2026-08-18 — Transcripción manual de metodología a YAML

**Decisión**: los perfiles de metodología se transcriben a mano por el
usuario a partir de la fuente original (libro, paper, apuntes), no por el
LLM.

**Por qué**: es el punto de mayor riesgo de que el sistema "invente"
metodología. Transcripción manual garantiza que cada regla en el sistema
existe porque un humano la verificó contra la fuente.

## 2026-08-18 — MCP como cliente, no como servidor

**Decisión**: el agente consume servidores MCP externos (ej. un MCP de
Strava) en vez de exponer su propio servidor MCP.

**Por qué**: el objetivo de aprendizaje incluye MCP como consumidor;
además el historial de entrenamiento ya vive en sistemas externos (Strava),
así que consumir su MCP es el camino más directo. Exponer un servidor MCP
propio queda abierto como posible extensión futura, no descartado.

## 2026-08-18 — n8n como orquestador del flujo completo

**Decisión**: n8n dispara el proceso (cron/webhook), invoca al agente y
gestiona notificaciones del resultado, en vez de limitarse a sincronizar
datos de Strava.

**Por qué**: mantiene la lógica de negocio (motor + agente) dentro del
proyecto Python, testeable y versionada, mientras n8n se ocupa de lo que
mejor hace: orquestación de flujo y notificaciones, sin lógica de dominio
dentro de los workflows.
