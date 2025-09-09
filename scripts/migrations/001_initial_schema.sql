-- Initial database schema migration
-- Creates the basic table structure for the gent_disagreement_processor

-- Enable vector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create episodes table
CREATE TABLE IF NOT EXISTS episodes (
    id SERIAL PRIMARY KEY,
    episode_number VARCHAR(20) NOT NULL UNIQUE,
    title TEXT,
    file_name VARCHAR(255),
    date_published DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create transcript_segments table with episode reference
CREATE TABLE IF NOT EXISTS transcript_segments (
    id SERIAL PRIMARY KEY,
    episode_id INTEGER REFERENCES episodes(id),
    speaker TEXT NOT NULL,
    text TEXT NOT NULL,
    embedding vector(1536)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_transcript_segments_episode_id ON transcript_segments(episode_id);
CREATE INDEX IF NOT EXISTS idx_transcript_segments_speaker ON transcript_segments(speaker);
CREATE INDEX IF NOT EXISTS idx_episodes_episode_number ON episodes(episode_number);
