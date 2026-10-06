# Graph Report - reel-digest  (2026-10-06)

## Corpus Check
- Corpus is ~2,242 words - fits in a single context window. You may not need a graph.

## Summary
- 102 nodes · 163 edges · 15 communities (4 shown, 11 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- CLI Interface & URL Processing
- Transcription & Note Exporting
- Architecture & Core Workflows
- LLM Summarization Pipeline
- Audio Downloader & Extraction
- Settings & FFmpeg Discovery
- Pipeline Unit Tests
- Project Root
- Pydantic Data Validation
- Pytest Framework
- Dotenv Management
- Rich Terminal UI
- Typer CLI Framework

## God Nodes (most connected - your core abstractions)
1. `ReelDigestPipeline` - 9 edges
2. `NoteExporter` - 9 edges
3. `AudioDownloader` - 8 edges
4. `SummaryResult` - 8 edges
5. `OmnirouteSummarizer` - 8 edges
6. `FasterWhisperTranscriber` - 8 edges
7. `process_url()` - 7 edges
8. `watch()` - 7 edges
9. `TranscriptResult` - 7 edges
10. `batch()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `process_url()` --calls--> `ReelDigestPipeline`  [EXTRACTED]
  main.py → reel_digest/pipeline.py
- `ReelDigestPipeline` --uses--> `NoteExporter`  [INFERRED]
  reel_digest/pipeline.py → reel_digest/storage.py
- `ReelDigestPipeline` --uses--> `OmnirouteSummarizer`  [INFERRED]
  reel_digest/pipeline.py → reel_digest/summarizer.py
- `ReelDigestPipeline` --uses--> `FasterWhisperTranscriber`  [INFERRED]
  reel_digest/pipeline.py → reel_digest/transcriber.py
- `NoteExporter` --uses--> `SummaryResult`  [INFERRED]
  reel_digest/storage.py → reel_digest/summarizer.py

## Import Cycles
- None detected.

## Communities (15 total, 11 thin omitted)

### Community 0 - "CLI Interface & URL Processing"
Cohesion: 0.15
Nodes (5): batch(), digest(), is_instagram_reel_url(), process_url(), watch()

### Community 1 - "Transcription & Note Exporting"
Cohesion: 0.16
Nodes (5): NoteExporter, BaseTranscriber, FasterWhisperTranscriber, TranscriptResult, TranscriptSegment

### Community 2 - "Architecture & Core Workflows"
Cohesion: 0.15
Nodes (13): AI Synthesis, Architecture Design, Automated Audio Extraction, Clipboard Watcher Mode, FasterWhisperTranscriber, ReelDigest, Structured Knowledge, av (+5 more)

### Community 3 - "LLM Summarization Pipeline"
Cohesion: 0.23
Nodes (3): BaseSummarizer, OmnirouteSummarizer, SummaryResult

## Knowledge Gaps
- **9 isolated node(s):** `reel-digest`, `Structured Knowledge`, `av`, `pydantic`, `python-dotenv` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 40 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ReelDigestPipeline` connect `Audio Downloader & Extraction` to `CLI Interface & URL Processing`, `Transcription & Note Exporting`, `LLM Summarization Pipeline`, `Environment & Configuration`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `ReelDigestPipeline` (e.g. with `AudioDownloader` and `NoteExporter`) actually correct?**
  _`ReelDigestPipeline` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `reel-digest`, `Structured Knowledge`, `av` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `AudioDownloader` connect `Audio Downloader & Extraction` to `Environment & Configuration`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `NoteExporter` (e.g. with `ReelDigestPipeline` and `SummaryResult`) actually correct?**
  _`NoteExporter` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Why does `NoteExporter` connect `Transcription & Note Exporting` to `LLM Summarization Pipeline`, `Environment & Configuration`, `Audio Downloader & Extraction`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._