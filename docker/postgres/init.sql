-- Se ejecuta una sola vez, cuando el volumen de Postgres está vacío.
-- Crea una base y un usuario por servicio; las contraseñas llegan por
-- variables de entorno (definidas en .env), nunca escritas aquí.

\getenv n8n_password N8N_DB_PASSWORD
\getenv pb_coach_password PB_COACH_DB_PASSWORD

CREATE USER n8n WITH PASSWORD :'n8n_password';
CREATE DATABASE n8n OWNER n8n;

CREATE USER pb_coach WITH PASSWORD :'pb_coach_password';
CREATE DATABASE pb_coach OWNER pb_coach;

-- Ninguno de los dos puede conectarse a la base del otro.
REVOKE CONNECT ON DATABASE n8n FROM PUBLIC;
REVOKE CONNECT ON DATABASE pb_coach FROM PUBLIC;
GRANT CONNECT ON DATABASE n8n TO n8n;
GRANT CONNECT ON DATABASE pb_coach TO pb_coach;
