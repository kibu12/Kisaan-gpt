-- ============================================================
-- KISAAN-GPT — One-time Supabase SQL setup
-- Run this entire script in your Supabase SQL Editor once.
-- ============================================================

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. RAG document chunks table
CREATE TABLE IF NOT EXISTS rag_documents (
    id          BIGSERIAL PRIMARY KEY,
    source      TEXT NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(384),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Cosine similarity search function
CREATE OR REPLACE FUNCTION match_documents (
    query_embedding  vector(384),
    match_threshold  FLOAT,
    match_count      INT
)
RETURNS TABLE (
    id         BIGINT,
    source     TEXT,
    content    TEXT,
    similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        id,
        source,
        content,
        1 - (embedding <=> query_embedding) AS similarity
    FROM rag_documents
    WHERE 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;

-- 4. Farm profiles table
CREATE TABLE IF NOT EXISTS farms (
    farm_id      TEXT PRIMARY KEY,
    farmer_name  TEXT,
    password_hash TEXT,
    location     TEXT,
    district     TEXT,
    area_acres   FLOAT,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Soil readings table (farm digital twin)
CREATE TABLE IF NOT EXISTS soil_readings (
    id                BIGSERIAL PRIMARY KEY,
    farm_id           TEXT REFERENCES farms(farm_id) ON DELETE CASCADE,
    reading_date      TIMESTAMPTZ DEFAULT NOW(),
    season            TEXT,
    n_val             FLOAT,
    p_val             FLOAT,
    k_val             FLOAT,
    ph                FLOAT,
    humidity          FLOAT,
    temperature       FLOAT,
    rainfall          FLOAT,
    ec                FLOAT,
    oc                FLOAT,
    recommended_crop  TEXT,
    confidence        FLOAT
);

-- 6. IVFFlat index — run AFTER inserting RAG data (requires ≥1 row)
-- CREATE INDEX IF NOT EXISTS rag_embedding_idx
--     ON rag_documents
--     USING ivfflat (embedding vector_cosine_ops)
--     WITH (lists = 100);

-- ============================================================
-- Uncomment and run the index creation after build_knowledge_base.py
-- ============================================================
