CREATE TABLE IF NOT EXISTS query_audit (
  request_id UUID PRIMARY KEY,
  user_id VARCHAR(120) NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  confidence DOUBLE PRECISION NOT NULL DEFAULT 0,
  escalation_required BOOLEAN NOT NULL DEFAULT FALSE,
  retrieved_chunk_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  latency_ms INTEGER NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_query_audit_user_id ON query_audit(user_id);
