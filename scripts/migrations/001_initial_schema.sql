-- Initial database schema migration
-- Creates the basic table structure for the gent_disagreement_rag

-- Enable vector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create speaker role enum
CREATE TYPE speaker_role_enum AS ENUM ('host', 'guest');

-- Create episodes table
CREATE TABLE IF NOT EXISTS episodes (
    episode_number INTEGER PRIMARY KEY,
    title TEXT,
    file_name VARCHAR(255),
    date_published DATE,
    is_processed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS speakers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS episode_speakers (
    id SERIAL PRIMARY KEY,
    episode_id INTEGER NOT NULL REFERENCES episodes(episode_number),
    speaker_id INTEGER NOT NULL REFERENCES speakers(id),
    speaker_number INTEGER NOT NULL,
    role speaker_role_enum,
    UNIQUE (episode_id, speaker_number),
    UNIQUE (episode_id, speaker_id)
);

-- Create transcript_segments table with episode reference
CREATE TABLE IF NOT EXISTS transcript_segments (
    id SERIAL PRIMARY KEY,
    episode_id INTEGER REFERENCES episodes(episode_number),
    speaker_id INTEGER NOT NULL REFERENCES speakers(id),
    text TEXT NOT NULL,
    embedding vector(1536)
);

-- NEXT STEP: UPDATE THE SEED FILE TO USE THE NEW SPEAKERS TABLE

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_transcript_segments_episode_id ON transcript_segments(episode_id);
CREATE INDEX IF NOT EXISTS idx_transcript_segments_speaker_id ON transcript_segments(speaker_id);
