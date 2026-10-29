-- Alembic owns application-table creation and schema evolution.
-- Keep this init script limited to database prerequisites for fresh installs.
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

GRANT CONNECT ON DATABASE sentinel_db TO sentinel_user;
GRANT USAGE, CREATE ON SCHEMA public TO sentinel_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO sentinel_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sentinel_user;
