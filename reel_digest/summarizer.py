from abc import ABC, abstractmethod
from typing import NamedTuple
from openai import OpenAI
from reel_digest.config import settings

class SummaryResult(NamedTuple):
    title: str
    tldr: str
    key_takeaways: list[str]
    research_ideas: list[str]
    memorable_quotes: list[str]
    suggested_tags: list[str]
    raw_markdown: str

class BaseSummarizer(ABC):
    @abstractmethod
    def summarize(self, transcript: str, original_title: str = "") -> SummaryResult:
        """Summarize transcript text."""
        pass

class OmnirouteSummarizer(BaseSummarizer):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None
    ):
        self.api_key = api_key or settings.omniroute_api_key or "no-key"
        self.base_url = base_url or settings.omniroute_base_url
        self.model = model or settings.omniroute_model

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def summarize(self, transcript: str, original_title: str = "") -> SummaryResult:
        system_prompt = (
            "You are an analytical researcher and idea synthesizer. "
            "You transform raw video transcripts into crisp, high-signal knowledge notes. "
            "Always output your analysis using structured sections: TL;DR, Key Takeaways, "
            "Research Ideas / Actionable Angles, Standout Quotes, and Tags."
        )

        user_prompt = f"""
Here is a transcript extracted from an Instagram Reel (Original caption/hook: "{original_title}"):

---
{transcript}
---

Please analyze and format your output in clean Markdown according to this exact structure:

# [Punchy, descriptive title summarizing the core insight]

## TL;DR
[1-2 sentences capturing the essence]

## 💡 Key Takeaways
- [Bullet 1]
- [Bullet 2]
- [Bullet 3]

## 🔬 Research & Actionable Angles
- [Actionable idea or research question sparked by this content]
- [Next step or connection to broader concepts]

## 💬 Standout Quotes
- "[Notable quote or punchline from the transcript]"

## 🏷️ Tags
`#tag1`, `#tag2`, `#tag3`
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
            )
            raw_markdown = response.choices[0].message.content or ""
            return self._parse_markdown(raw_markdown, original_title)
        except Exception as e:
            # Fallback if API fails or is unconfigured
            fallback_md = f"# Summary of: {original_title or 'Instagram Reel'}\n\n*API Summary unavailable: {str(e)}*\n\n### Transcript Preview\n{transcript[:300]}..."
            return SummaryResult(
                title=original_title or "Instagram Reel Note",
                tldr="Summary unavailable (API call error)",
                key_takeaways=["Transcription succeeded, but summarizer encountered an error."],
                research_ideas=[],
                memorable_quotes=[],
                suggested_tags=["reel", "idea"],
                raw_markdown=fallback_md
            )

    def _parse_markdown(self, md: str, default_title: str) -> SummaryResult:
        lines = md.strip().split("\n")
        title = default_title or "Instagram Reel Note"
        for line in lines:
            if line.startswith("# "):
                title = line.replace("# ", "").strip()
                break

        return SummaryResult(
            title=title,
            tldr="",
            key_takeaways=[],
            research_ideas=[],
            memorable_quotes=[],
            suggested_tags=[],
            raw_markdown=md
        )
