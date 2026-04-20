CREATE TABLE IF NOT EXISTS documents (
  doc_id UUID PRIMARY KEY,
  title VARCHAR(300) NOT NULL,
  policy_type VARCHAR(100) NOT NULL,
  version VARCHAR(50) NOT NULL DEFAULT 'v1',
  effective_date DATE NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'active',
  uploaded_by VARCHAR(120) NOT NULL,
  source_filename VARCHAR(500) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_policy_type ON documents(policy_type);
