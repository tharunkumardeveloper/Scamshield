-- ScamShield Honeypot API - Supabase Database Setup
-- Run this in Supabase SQL Editor

-- Create honeypot_conversations table
CREATE TABLE IF NOT EXISTS honeypot_conversations (
  id SERIAL PRIMARY KEY,
  conversation_id TEXT UNIQUE NOT NULL,
  scam_detected BOOLEAN DEFAULT FALSE,
  confidence_score FLOAT DEFAULT 0.0,
  scam_type TEXT,
  extracted_intelligence JSONB,
  engagement_metrics JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversation_id ON honeypot_conversations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_scam_detected ON honeypot_conversations(scam_detected);
CREATE INDEX IF NOT EXISTS idx_created_at ON honeypot_conversations(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE honeypot_conversations ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (for development)
CREATE POLICY "Allow all operations on honeypot_conversations" ON honeypot_conversations
  FOR ALL USING (true) WITH CHECK (true);
