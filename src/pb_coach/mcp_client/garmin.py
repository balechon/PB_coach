# Cliente MCP que consume el servidor garmin-mcp (Taxuspt/garmin_mcp), que
# corre como contenedor propio en la red interna del docker-compose.
#
# Dos usos, ambos deterministas (sin LLM), con una lista blanca de tools:
#   - sync: actividades nuevas -> SesionRealizada -> Postgres
#   - publicar: sesiones de la próxima semana -> entrenamientos en el reloj
#
# Placeholder — sin implementar todavía.
