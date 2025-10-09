# Pipeline Orchestrator Refactoring Plan

## Overview
This document outlines step-by-step improvements to refactor the `PipelineOrchestrator.process_episodes()` method to reduce duplication, improve maintainability, add error handling, and support both production and debugging workflows.

## Current Issues
1. **Code duplication** between `process_episodes()` and `format_existing_raw_transcripts()`
2. **No error handling** - one failed episode stops entire pipeline
3. **No progress visibility** - minimal logging of pipeline stages
4. **Missing validation** - no checks for required episode fields
5. **Inflexible data flow** - always reloads from disk (inefficient for production)
6. **Poor testability** - monolithic methods hard to unit test

---

## Refactoring Steps

### Step 1: Add Configurable Disk Reload Flag
**Goal:** Support both production efficiency and debugging needs

**Changes:**
- Add `reload_from_disk: bool = False` parameter to `__init__()`
- Store as instance variable `self.reload_from_disk`
- Document that `True` enables validation of export/load roundtrip for debugging

**File:** `src/gent_disagreement_rag/core/pipeline_orchestrator.py:14-28`

**Benefits:**
- Production: optimized (no unnecessary disk I/O)
- Development: validates serialization roundtrip works correctly
- Explicit intent in code

---

### Step 2: Extract Episode Skip Logic
**Goal:** Eliminate duplicate skip checking code

**Changes:**
- Create private method `_should_skip_episode(self, episode) -> bool`
- Move lines 33-37 logic into this method
- Return `True` if episode should be skipped, `False` otherwise
- Include the print statement in the method

**Current duplicated code:**
```python
# Lines 33-37 and 65-69
if episode.get("processed", False):
    print(f"⏭️  Skipping episode {episode['episode_id']} - already processed")
    continue
```

**New method signature:**
```python
def _should_skip_episode(self, episode: dict) -> bool:
    """
    Check if episode has already been processed.

    Args:
        episode: Episode dictionary with metadata

    Returns:
        True if episode should be skipped, False otherwise
    """
```

**Benefits:**
- Single source of truth for skip logic
- Easier to modify skip conditions in future
- More testable

---

### Step 3: Extract Format and Export Logic
**Goal:** Reuse transcript formatting logic between methods

**Changes:**
- Create private method `_format_and_export_transcript(self, raw_transcript_path, speakers_map) -> str`
- Move formatting and export logic (lines 47-54 and 75-82) into this method
- Return the processed transcript path

**Current duplicated code:**
```python
# Format the transcript data
formatted_segments = self.transcript_formatter.format_segments(
    raw_transcript_path, speakers_map
)

# Export the formatted data
processed_transcript_path = self.transcript_exporter.export_segments(
    formatted_segments, raw_transcript_path.stem
)
```

**New method signature:**
```python
def _format_and_export_transcript(
    self, raw_transcript_path: Path, speakers_map: dict
) -> tuple[list[dict], str]:
    """
    Format raw transcript segments and export to JSON.

    Args:
        raw_transcript_path: Path to raw transcript JSON file
        speakers_map: Dictionary mapping speaker IDs to names

    Returns:
        Tuple of (formatted_segments, processed_transcript_path)
    """
```

**Note:** Return both `formatted_segments` and `processed_transcript_path` to support both production and debug workflows.

**Benefits:**
- Eliminates duplicate formatting logic
- Centralized formatting behavior
- Returns both segments and path for flexibility

---

### Step 4: Add Input Validation
**Goal:** Fail fast with clear errors if episode data is malformed

**Changes:**
- Create private method `_validate_episode(self, episode) -> None`
- Check for required fields: `episode_id`, `file_name`, `speakers_map`
- Raise `ValueError` with descriptive message if validation fails

**New method signature:**
```python
def _validate_episode(self, episode: dict) -> None:
    """
    Validate that episode dictionary contains required fields.

    Args:
        episode: Episode dictionary to validate

    Raises:
        ValueError: If required fields are missing
    """
```

**Required fields for `process_episodes`:**
- `episode_id`
- `file_name`
- `speakers_map`

**Required fields for `format_existing_raw_transcripts`:**
- `episode_id`
- `speakers_map`
- `raw_transcript_path`

**Benefits:**
- Clear error messages for configuration issues
- Prevents cryptic KeyError exceptions
- Documents expected episode structure

---

### Step 5: Extract Single Episode Processing Logic
**Goal:** Encapsulate full pipeline for one episode, enable unit testing

**Changes:**
- Create private method `_process_single_episode(self, episode) -> None`
- Move core pipeline logic (transcribe → format → embed → store)
- Use `self.reload_from_disk` flag to conditionally reload from disk
- Call `_validate_episode()` at the start

**New method signature:**
```python
def _process_single_episode(self, episode: dict) -> None:
    """
    Process a single episode through the full pipeline.

    Pipeline stages:
    1. Validate episode structure
    2. Transcribe audio file
    3. Format transcript segments
    4. Export formatted segments
    5. Generate embeddings (reload from disk if configured)
    6. Store embeddings in database

    Args:
        episode: Episode dictionary with metadata

    Raises:
        ValueError: If episode validation fails
        Exception: If any pipeline stage fails
    """
```

**Implementation detail:**
```python
# Generate embeddings - reload from disk if configured for debugging
if self.reload_from_disk:
    segments = load_processed_segments(Path(processed_transcript_path))
    embeddings = self.embedding_service.generate_embeddings(segments)
else:
    # Use in-memory segments for efficiency
    embeddings = self.embedding_service.generate_embeddings(formatted_segments)
```

**Benefits:**
- Testable in isolation
- Clear single responsibility
- Supports both production and debug modes

---

### Step 6: Extract Single Episode Formatting Logic
**Goal:** Encapsulate format-only pipeline for existing transcripts

**Changes:**
- Create private method `_format_single_episode(self, episode) -> None`
- Move format-only logic from `format_existing_raw_transcripts`
- Validate episode has `raw_transcript_path` field

**New method signature:**
```python
def _format_single_episode(self, episode: dict) -> None:
    """
    Format an existing raw transcript for a single episode.

    Pipeline stages:
    1. Validate episode structure (requires raw_transcript_path)
    2. Format transcript segments
    3. Export formatted segments

    Args:
        episode: Episode dictionary with metadata including raw_transcript_path

    Raises:
        ValueError: If episode validation fails
        Exception: If formatting/export fails
    """
```

**Benefits:**
- Mirrors `_process_single_episode` structure
- Testable in isolation
- Clear separation from full pipeline

---

### Step 7: Add Comprehensive Error Handling
**Goal:** Prevent one failed episode from stopping entire pipeline

**Changes:**
- Wrap `_process_single_episode()` and `_format_single_episode()` calls in try-except blocks
- Log errors with episode context
- Continue processing remaining episodes
- Track and report failed episodes at the end

**Implementation pattern:**
```python
def process_episodes(self):
    """Process all unprocessed episodes through full pipeline."""
    failed_episodes = []

    for episode in self.episodes:
        if self._should_skip_episode(episode):
            continue

        try:
            self._process_single_episode(episode)
        except Exception as e:
            episode_id = episode.get('episode_id', 'unknown')
            self.logger.error(f"Failed to process episode {episode_id}: {e}")
            failed_episodes.append((episode_id, str(e)))

    if failed_episodes:
        self.logger.warning(f"Failed to process {len(failed_episodes)} episode(s)")
        for episode_id, error in failed_episodes:
            self.logger.warning(f"  - Episode {episode_id}: {error}")
```

**Benefits:**
- Resilient pipeline (one failure doesn't stop all)
- Clear error reporting
- Visibility into what succeeded/failed

---

### Step 8: Simplify Public Methods
**Goal:** Make public interface clean and readable

**Changes:**
- Refactor `process_episodes()` to simple loop calling `_process_single_episode()`
- Refactor `format_existing_raw_transcripts()` to simple loop calling `_format_single_episode()`
- Both methods become ~10-15 lines with error handling

**New `process_episodes` structure:**
```python
def process_episodes(self):
    """Process all unprocessed episodes through the full pipeline."""
    failed_episodes = []

    for episode in self.episodes:
        if self._should_skip_episode(episode):
            continue

        try:
            self._process_single_episode(episode)
        except Exception as e:
            # error handling logic

    # report failures if any
```

**Benefits:**
- Clear high-level flow
- Easy to understand at a glance
- Complexity moved to focused private methods

---

### Step 9: Add Enhanced Logging
**Goal:** Provide visibility into pipeline progress

**Changes:**
- Add logging statements at start/completion of each major stage
- Log overall progress (e.g., "Processing episode 3/10")
- Use appropriate log levels (INFO for progress, ERROR for failures)

**Example logging additions:**
```python
self.logger.info(f"Processing episode {idx+1}/{total}: {episode_id}")
self.logger.info(f"✓ Transcription complete for {episode_id}")
self.logger.info(f"✓ Generated {len(embeddings)} embeddings for {episode_id}")
self.logger.info(f"✓ Stored embeddings for {episode_id}")
```

**Benefits:**
- Easier debugging
- Progress visibility for long-running pipelines
- Audit trail of processing

---

## Implementation Order

Recommended order to minimize conflicts:

1. **Step 1** - Add reload flag (minimal change, sets foundation)
2. **Step 2** - Extract skip logic (safe, no dependencies)
3. **Step 4** - Add validation (safe, no dependencies)
4. **Step 3** - Extract format/export (safe, used by later steps)
5. **Step 5** - Extract single episode processing (uses Steps 1, 3, 4)
6. **Step 6** - Extract single episode formatting (uses Steps 3, 4)
7. **Step 7** - Add error handling (depends on Steps 5, 6)
8. **Step 8** - Simplify public methods (depends on Steps 2, 5, 6, 7)
9. **Step 9** - Add enhanced logging (final polish)

---

## Testing Strategy

After each step, verify:
- Existing functionality still works
- No regressions in pipeline behavior
- New code paths are covered

**Key test scenarios:**
1. Process new episode from scratch
2. Skip already processed episode
3. Format existing raw transcript
4. Handle missing required fields
5. Recover from mid-pipeline failure
6. Validate disk reload vs in-memory paths

---

## Success Criteria

- [ ] Code duplication eliminated
- [ ] All episodes process successfully with error handling
- [ ] Pipeline resilient to individual episode failures
- [ ] Clear logging of progress and errors
- [ ] Support for both production and debug workflows
- [ ] Improved testability (can test stages in isolation)
- [ ] Public methods under 15 lines each
- [ ] All tests pass
