#!/bin/bash
# Initialize replication user and settings

set -e

# Create replication user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create replication user
    CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD '${REPLICATION_PASSWORD}';
    
    -- Grant necessary permissions
    GRANT CONNECT ON DATABASE sentinel TO replicator;
    
    -- Create replication slot for replica
    SELECT pg_create_physical_replication_slot('replica_slot');
EOSQL

echo "Replication user and slot created successfully"
