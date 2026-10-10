import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from reel_digest.config import settings
from reel_digest.transcriber import TranscriptResult
from reel_digest.summarizer import SummaryResult
from reel_digest.platform import PlatformMetadata

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
        platform_metadata: Optional[PlatformMetadata] = None,
    ) -> str:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = self._sanitize_filename(summary_result.title or title)

        # Use platform-specific output organization if metadata is provided
        if platform_metadata:
            platform_name = platform_metadata.platform.value
            file_path = settings.get_output_path(f"{file_date}_{safe_title}.md", platform_name)
        else:
            filename = f"{file_date}_{safe_title}.md"
            file_path = self.output_dir / filename

        # Format timestamped segments
        segments_md_list = []
        for s in transcript_result.segments:
            start_m, start_s = divmod(int(s.start), 60)
            end_m, end_s = divmod(int(s.end), 60)
            segments_md_list.append(f"- **[{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}]** {s.text}")
        timestamped_transcript = "\n".join(segments_md_list)

        # Build YAML frontmatter with platform metadata
        frontmatter_lines = [
            f'title: "{summary_result.title or title}"',
            f'date: {date_str}',
            f'url: "{url}"',
            f'language: "{transcript_result.language}"',
            f'duration_seconds: {transcript_result.duration:.2f}',
        ]

        if platform_metadata:
            frontmatter_lines.append(f'platform: "{platform_metadata.platform.value}"')
            frontmatter_lines.append(f'source: "{platform_metadata.platform.value.title()}"')

            # Add additional metadata if available
            if platform_metadata.author:
                frontmatter_lines.append(f'author: "{platform_metadata.author}"')
            if platform_metadata.video_id:
                frontmatter_lines.append(f'video_id: "{platform_metadata.video_id}"')
            if platform_metadata.upload_date:
                frontmatter_lines.append(f'upload_date: "{platform_metadata.upload_date}"')
            if platform_metadata.view_count:
                frontmatter_lines.append(f'view_count: {platform_metadata.view_count}')
        else:
            # Fallback for backward compatibility
            frontmatter_lines.append('source: "Instagram Reel"')

        frontmatter_lines.append('type: "research-note"')

        # Join frontmatter lines
        frontmatter = "\n".join(frontmatter_lines)

        markdown_content = f"""---
{frontmatter}
---

{summary_result.raw_markdown}

---

## 📜 Full Transcript

### Timestamped Segments
{timestamped_transcript}

### Continuous Text
> {transcript_result.text}
"""

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(markdown_content, encoding="utf-8")
        return str(file_path.absolute())
