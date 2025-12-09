-- Supabase Database Schema for CTF Scoreboard
-- Run this SQL in your Supabase SQL Editor

-- Create scoreboard table
CREATE TABLE IF NOT EXISTS scoreboard (
    id BIGSERIAL PRIMARY KEY,
    rank INTEGER NOT NULL,
    team_id INTEGER UNIQUE NOT NULL,
    team_name TEXT NOT NULL,
    score INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on rank for faster queries
CREATE INDEX IF NOT EXISTS idx_scoreboard_rank ON scoreboard(rank);

-- Create index on team_id for faster upserts
CREATE INDEX IF NOT EXISTS idx_scoreboard_team_id ON scoreboard(team_id);

-- Create index on score for sorting
CREATE INDEX IF NOT EXISTS idx_scoreboard_score ON scoreboard(score DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE scoreboard ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public read access
CREATE POLICY "Allow public read access" 
ON scoreboard FOR SELECT 
TO anon 
USING (true);

-- Create policy to allow authenticated users to insert/update
CREATE POLICY "Allow authenticated insert/update" 
ON scoreboard FOR ALL 
TO authenticated 
USING (true) 
WITH CHECK (true);

-- Optional: Create a function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_scoreboard_updated_at 
BEFORE UPDATE ON scoreboard 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE scoreboard IS 'Stores CTF competition scoreboard data';
COMMENT ON COLUMN scoreboard.rank IS 'Current rank of the team';
COMMENT ON COLUMN scoreboard.team_id IS 'Unique team identifier from CTFd';
COMMENT ON COLUMN scoreboard.team_name IS 'Name of the team';
COMMENT ON COLUMN scoreboard.score IS 'Total score of the team';
