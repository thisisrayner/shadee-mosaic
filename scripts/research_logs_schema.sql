-- Create a new table to log research queries and responses for analytical tracking.
CREATE TABLE IF NOT EXISTS research_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    query_text TEXT NOT NULL,
    response_text TEXT,
    query_type TEXT NOT NULL CHECK (query_type IN ('primary', 'followup')),
    n_used INTEGER,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- Enable RLS (standard for Supabase) but allowing service role to bypass
ALTER TABLE research_logs ENABLE ROW LEVEL SECURITY;

-- Add comment for future developers
COMMENT ON TABLE research_logs IS 'Logs of user research queries and AI responses to aid in feature development and thematic tracking.';
