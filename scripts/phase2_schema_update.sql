-- Non-destructive schema update for Project Shadee-Intelligence
-- Adds "Shadow Tracking" columns to support Phase 2 & 3.

-- 1. Add Anonymization Flag
ALTER TABLE social_posts 
ADD COLUMN IF NOT EXISTS is_anonymized BOOLEAN DEFAULT FALSE;

-- 2. Add Verified Bucket ID (Source of Truth)
ALTER TABLE social_posts 
ADD COLUMN IF NOT EXISTS verified_bucket_id TEXT;

-- 3. Add Shadow Content Column (PRESERVES ORIGINAL CONTENT)
ALTER TABLE social_posts 
ADD COLUMN IF NOT EXISTS content_scrubbed TEXT;

-- 4. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 5. Add Embedding Column
-- Using 768 dimensions for Google Gemini text-embedding-004
-- Or 1536 for OpenAI text-embedding-3-small
-- We'll use 768 for now as Gemini is our primary LLM provider
-- 7. Vector Similarity Search Function
-- This enables RPC calls from our Python SDK to perform semantic search
-- NOTE: We drop first because PostgreSQL doesn't allow changing return types with CREATE OR REPLACE
DROP FUNCTION IF EXISTS match_social_posts(vector, float, int);
DROP FUNCTION IF EXISTS match_social_posts(vector, float, int, text);

CREATE OR REPLACE FUNCTION match_social_posts (
  query_embedding vector(768),
  match_threshold float,
  match_count int,
  filter_region text DEFAULT NULL
)
RETURNS TABLE (
  id uuid,
  content_scrubbed text,
  content text,
  platform text,
  post_dt timestamptz,
  region text,
  bucket_id text,
  ai_bucket_id text,
  ai_explanation text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    social_posts.id,
    social_posts.content_scrubbed,
    social_posts.content,
    social_posts.platform,
    social_posts.post_dt,
    social_posts.region,
    social_posts.bucket_id,
    social_posts.ai_bucket_id,
    social_posts.ai_explanation,
    1 - (social_posts.embedding <=> query_embedding) AS similarity
  FROM social_posts
  WHERE 1 - (social_posts.embedding <=> query_embedding) > match_threshold
  AND (
    filter_region IS NULL 
    OR (filter_region = 'Singapore' AND social_posts.region IN ('Singapore', 'SG'))
    OR (social_posts.region = filter_region)
  )
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
