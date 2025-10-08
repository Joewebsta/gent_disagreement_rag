# Parallel Episode Processing Implementation Plan

## Overview

Enable concurrent processing of multiple podcast episodes to significantly reduce total processing time. Each episode undergoes independent stages (transcription, formatting, embedding generation, database storage) that can be parallelized at the episode level.

## Current Architecture

The current sequential implementation in `main.py:46-74` processes episodes one at a time:

```python
for episode in episodes:
    # 1. Audio transcription (Deepgram API call)
    raw_transcript_path = audio_transcriber.generate_transcript(file_name)

    # 2. Formatting (local processing)
    formatted_segments = formatter.format_segments(raw_transcript_path)

    # 3. Export (file I/O)
    processed_transcript_path = exporter.export_segments(...)

    # 4. Embedding generation (OpenAI API calls)
    embeddings = embedding_service.generate_embeddings(segments)

    # 5. Database storage (PostgreSQL writes)
    database_manager.store_embeddings(embeddings, episode_id)
```

## Parallelization Strategy

### Episode-Level Parallelization

**Why this works:**
- Each episode is completely independent
- No shared state between episodes (except DB connection)
- Most time spent on I/O-bound API calls (Deepgram, OpenAI)
- ThreadPoolExecutor ideal for I/O-bound workloads

**Benefits:**
- Process 3-4 episodes concurrently
- Reduce total processing time by ~75% (for 4 parallel workers)
- Maintain code simplicity with `concurrent.futures`

## Implementation Steps

### 1. Update DatabaseManager for Connection Pooling

**File:** `src/gent_disagreement_rag/core/database_manager.py`

**Changes:**
- Import `psycopg2.pool.SimpleConnectionPool`
- Create connection pool in `__init__()` instead of single connection
- Update `get_connection()` to acquire from pool
- Add `return_connection()` method to release back to pool
- Ensure `store_embeddings()` properly returns connections

**Example:**
```python
from psycopg2.pool import SimpleConnectionPool

class DatabaseManager:
    def __init__(self, ..., min_connections=1, max_connections=5):
        # ... existing code ...
        self.connection_pool = SimpleConnectionPool(
            min_connections,
            max_connections,
            **self.connection_params
        )

    def get_connection(self):
        return self.connection_pool.getconn()

    def return_connection(self, conn):
        self.connection_pool.putconn(conn)

    def store_embeddings(self, embeddings, episode_id):
        conn = self.get_connection()
        try:
            # ... existing logic ...
        finally:
            self.return_connection(conn)
```

### 2. Create Episode Processing Worker Function

**File:** `src/gent_disagreement_rag/main.py`

**Changes:**
- Extract episode processing logic into `process_episode()` function
- Accept episode dict and service instances as parameters
- Return success/failure status with error details
- Add proper logging for parallel execution tracking

**Example:**
```python
def process_episode(
    episode: dict,
    audio_transcriber: AudioTranscriber,
    formatter: TranscriptFormatter,
    exporter: TranscriptExporter,
    embedding_service: EmbeddingService,
    database_manager: DatabaseManager
) -> dict:
    """Process a single episode through the full pipeline."""
    try:
        episode_id = episode["episode_id"]
        file_name = episode["file_name"]

        print(f"[Episode {episode_id}] Starting processing...")

        # Transcribe audio
        raw_transcript_path = audio_transcriber.generate_transcript(file_name)
        if not raw_transcript_path:
            raise Exception("Transcription failed")

        # Format segments
        formatted_segments = formatter.format_segments(raw_transcript_path)

        # Export
        processed_transcript_path = exporter.export_segments(
            formatted_segments, raw_transcript_path.stem
        )

        # Generate embeddings
        segments = load_processed_segments(Path(processed_transcript_path))
        embeddings = embedding_service.generate_embeddings(segments)

        # Store in database
        database_manager.store_embeddings(embeddings, episode_id)

        print(f"[Episode {episode_id}] ✅ Completed successfully")
        return {"episode_id": episode_id, "status": "success", "error": None}

    except Exception as e:
        print(f"[Episode {episode_id}] ❌ Failed: {e}")
        return {"episode_id": episode_id, "status": "failed", "error": str(e)}
```

### 3. Update main() for Parallel Execution

**File:** `src/gent_disagreement_rag/main.py`

**Changes:**
- Use `concurrent.futures.ThreadPoolExecutor`
- Configure max workers from environment variable
- Filter unprocessed episodes before submission
- Track results and report summary

**Example:**
```python
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

def main():
    """Main execution function with parallel episode processing."""

    # Get max workers from env (default: 3)
    max_workers = int(os.getenv("MAX_PARALLEL_EPISODES", "3"))

    # Initialize database manager with connection pooling
    database_manager = DatabaseManager(max_connections=max_workers + 2)

    # Verify database connection
    try:
        conn = database_manager.get_connection()
        database_manager.return_connection(conn)
    except Exception as e:
        print("❌ Database connection failed!")
        print("Please run 'poetry run seed-db' to set up the database first.")
        print(f"Error: {e}")
        return

    # Initialize services (these are thread-safe for reading)
    audio_transcriber = AudioTranscriber()
    formatter = TranscriptFormatter()
    exporter = TranscriptExporter()
    embedding_service = EmbeddingService()

    # Load and filter episodes
    episodes = load_episodes()
    unprocessed_episodes = [
        ep for ep in episodes if not ep.get("processed", False)
    ]

    if not unprocessed_episodes:
        print("✅ All episodes already processed!")
        return

    print(f"📊 Processing {len(unprocessed_episodes)} episodes with {max_workers} parallel workers")

    # Create partial function with service instances
    worker_func = partial(
        process_episode,
        audio_transcriber=audio_transcriber,
        formatter=formatter,
        exporter=exporter,
        embedding_service=embedding_service,
        database_manager=database_manager
    )

    # Process episodes in parallel
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_episode = {
            executor.submit(worker_func, episode): episode
            for episode in unprocessed_episodes
        }

        # Collect results as they complete
        for future in as_completed(future_to_episode):
            result = future.result()
            results.append(result)

    # Report summary
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]

    print("\n" + "="*50)
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")

    if failed:
        print("\nFailed episodes:")
        for r in failed:
            print(f"  - Episode {r['episode_id']}: {r['error']}")
```

### 4. Add Configuration Support

**File:** `.env`

**Add:**
```bash
# Parallel processing configuration
MAX_PARALLEL_EPISODES=3  # Recommended: 2-4 based on system resources
```

**File:** `CLAUDE.md` (update documentation)

Add section explaining parallel processing configuration:
```markdown
## Performance Configuration

### Parallel Episode Processing

Control concurrent episode processing with:
```bash
MAX_PARALLEL_EPISODES=3  # Default: 3 concurrent episodes
```

Recommendations:
- **2-3 workers**: Good for most systems, balances speed vs resource usage
- **4+ workers**: May hit API rate limits or memory constraints
- **1 worker**: Disables parallelization (sequential processing)
```

### 5. Enhanced Error Handling

**Considerations:**
- Individual episode failures don't crash entire pipeline
- Failed episodes can be retried by unmarking them in `episodes.json`
- Detailed error messages for debugging
- Summary report shows which episodes succeeded/failed

## API Rate Limit Considerations

### OpenAI Embeddings
- **Current approach**: Sequential API calls per segment
- **Improvement opportunity**: Use batch embeddings API
- **Rate limit safety**: OpenAI client handles retries automatically
- **Recommendation**: Start with 3 workers, monitor for rate limit errors

### Deepgram Transcription
- Concurrent requests generally supported
- Each episode = 1 transcription request
- Unlikely to hit limits with 3-4 parallel episodes

## Memory Considerations

- Audio files loaded one at a time per worker
- Each worker maintains independent transcript/embedding data
- Connection pool limits database connections
- **Recommendation**: Monitor memory usage with 3+ workers

## Testing Strategy

1. Test with `MAX_PARALLEL_EPISODES=1` (verify sequential still works)
2. Test with `MAX_PARALLEL_EPISODES=2` (basic parallelization)
3. Test with `MAX_PARALLEL_EPISODES=4` (stress test)
4. Verify database connection pool handles concurrent writes
5. Test error handling with intentionally failing episodes

## Migration Path

1. Implement connection pooling in `DatabaseManager`
2. Add `process_episode()` worker function
3. Update `main()` with ThreadPoolExecutor (keep sequential as fallback)
4. Test with existing processed episodes marked as unprocessed
5. Document configuration in README
6. Consider adding `--parallel` CLI flag for explicit control

## Future Enhancements

- **Batch embedding API**: Process all segments in one API call (faster, cheaper)
- **Progress tracking**: Real-time progress bars for each worker
- **Resume capability**: Track partially processed episodes
- **Dynamic worker scaling**: Adjust workers based on system load
- **Async/await**: Consider `asyncio` for even better I/O concurrency
