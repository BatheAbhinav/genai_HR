CREATE TABLE IF NOT EXISTS chunks (
  chunk_id UUID PRIMARY KEY,
  doc_id UUID NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  chunk_text TEXT NOT NULL,
  page_number INTEGER NULL,
  section VARCHAR(200) NULL,
  policy_type VARCHAR(100) NOT NULL,
  version VARCHAR(50) NOT NULL,
  embedding VECTOR(768) NOT NULL,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_chunks_policy_type ON chunks(policy_type);
