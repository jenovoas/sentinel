CREATE TABLE IF NOT EXISTS deployment_operations (
    operation_id text PRIMARY KEY,
    tenant_id text NOT NULL,
    request_id text NOT NULL,
    service_id text NOT NULL,
    template text NOT NULL,
    config jsonb NOT NULL,
    idempotency_key text NOT NULL,
    payload_fingerprint char(64) NOT NULL,
    status text NOT NULL CHECK (status IN ('preparing','deploying','verifying','available','blocked','failed')),
    public_url text,
    error_code text CHECK (error_code IS NULL OR error_code = 'deployment_precondition_failed'),
    lease_owner text,
    lease_until timestamptz,
    attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    destroyed_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, idempotency_key)
);
CREATE INDEX IF NOT EXISTS deployment_operations_claim_idx
    ON deployment_operations(status, lease_until, created_at)
    WHERE status IN ('preparing','deploying','verifying');
CREATE INDEX IF NOT EXISTS deployment_operations_tenant_operation_idx
    ON deployment_operations(tenant_id, operation_id);

CREATE UNIQUE INDEX IF NOT EXISTS deployment_one_live_operation_per_tenant_idx
    ON deployment_operations(tenant_id)
    WHERE status IN ('preparing','deploying','verifying','available','failed')
      AND destroyed_at IS NULL;
CREATE TABLE IF NOT EXISTS terraform_states (
    state_key text PRIMARY KEY,
    ciphertext bytea NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS terraform_state_locks (
    state_key text PRIMARY KEY,
    lock_id text NOT NULL,
    lock_info jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION deployment_status_is_monotonic() RETURNS trigger AS $$
DECLARE
    old_rank integer;
    new_rank integer;
BEGIN
    old_rank := CASE OLD.status WHEN 'preparing' THEN 0 WHEN 'deploying' THEN 1 WHEN 'verifying' THEN 2 ELSE 3 END;
    new_rank := CASE NEW.status WHEN 'preparing' THEN 0 WHEN 'deploying' THEN 1 WHEN 'verifying' THEN 2 ELSE 3 END;
    IF new_rank < old_rank OR (old_rank = 3 AND NEW.status <> OLD.status) THEN
        RAISE EXCEPTION 'non_monotonic_deployment_status';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS deployment_status_monotonic ON deployment_operations;
CREATE TRIGGER deployment_status_monotonic
    BEFORE UPDATE OF status ON deployment_operations
    FOR EACH ROW EXECUTE FUNCTION deployment_status_is_monotonic();
CREATE TABLE IF NOT EXISTS tenant_storage_purges (
    tenant_id text PRIMARY KEY,
    created_at timestamptz NOT NULL DEFAULT now(),
    purged_at timestamptz
);
