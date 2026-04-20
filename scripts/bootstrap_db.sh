#!/usr/bin/env bash
set -euo pipefail

psql "$DATABASE_URL" -f migrations/001_enable_pgvector.sql
psql "$DATABASE_URL" -f migrations/002_create_documents.sql
psql "$DATABASE_URL" -f migrations/003_create_chunks.sql
psql "$DATABASE_URL" -f migrations/004_create_query_audit.sql
