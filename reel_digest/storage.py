import re
from datetime import datetime
from pathlib import Path
from reel_digest.config import settings
from reel_digest.transcriber import TranscriptResult
from reel_digest.summarizer import SummaryResult

class NoteExporter:
    def __init__(self, output_dir: str | Path | None = None):
        self.output_dir = Path(output_dir) if output_dir else settings.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, text: str) -> str:
        # Keep alphanumeric, spaces, dashes and underscores
        cleaned = re.sub(r'[^\w\s-]', '', text).strip()
        cleaned = re.sub(r'[-\s]+', '-', cleaned)
        return cleaned[:50] or "reel-digest"

    def export(
        self,
        url: str,
        title: str,
        transcript_result: TranscriptResult,
        summary_result: SummaryResult,
    ) -> str:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = self._sanitize_filename(summary_result.title or title)
        filename = f"{file_date}_{safe_title}.md"
        file_path = self.output_dir / filename

        # Format timestamped segments
        segments_md_list = []
        for s in transcript_result.segments:
            start_m, start_s = divmod(int(s.start), 60)
            end_m, end_s = divmod(int(s.end), 60)
            segments_md_list.append(f"- **[{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}]** {s.text}")
        timestamped_transcript = "\n".join(segments_md_list)

        markdown_content = f"""---
title: "{summary_result.title or title}"
date: {date_str}
url: "{url}"
language: "{transcript_result.language}"
duration_seconds: {transcript_result.duration:.2f}
source: "Instagram Reel"
type: "research-note"
---

{summary_result.raw_markdown}

---

## 📜 Full Transcript

### Timestamped Segments
{timestamped_transcript}

### Continuous Text
> {transcript_result.text}
"""

        file_path.write_text(markdown_content, encoding="utf-8")
        return str(file_path.absolute())
