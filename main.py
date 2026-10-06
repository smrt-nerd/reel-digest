import sys
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import time
import re
from pathlib import Path
import typer
import pyperclip
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from reel_digest.pipeline import ReelDigestPipeline
from reel_digest.config import settings

app = typer.Typer(
    name="reel",
    help="ReelDigest CLI: Automated Instagram Reel Audio & Idea Extraction",
    add_completion=False,
)

console = Console()

def is_instagram_reel_url(text: str) -> bool:
    """Basic validation for Instagram Reel URLs."""
    if not text:
        return False
    return "instagram.com/reel/" in text or "instagram.com/p/" in text

def process_url(url: str):
    """Orchestrates the pipeline with a rich progress spinner."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Initializing...", total=None)

            def update_progress(msg: str):
                progress.update(task, description=f"[cyan]{msg}")

            pipeline = ReelDigestPipeline(progress_callback=update_progress)
            note_path = pipeline.process(url)

        console.print(f"\n[bold green]✓ Done![/bold green] Results saved to:\n[bold blue]{note_path}[/bold blue]\n")
    except Exception as e:
        console.print(f"\n[bold red]✖ Error processing {url}:[/bold red] {e}")

@app.command()
def digest(url: str = typer.Argument(..., help="The Instagram Reel URL to process")):
    """Process a single Instagram Reel URL."""
    if not is_instagram_reel_url(url):
        console.print("[bold yellow]Warning:[/bold yellow] This doesn't look like a standard Instagram URL, but attempting anyway...")
    process_url(url)

@app.command()
def batch(file_path: Path = typer.Argument(..., help="Text file containing one URL per line", exists=True)):
    """Process multiple Reels from a text file."""
    urls = [line.strip() for line in file_path.read_text().splitlines() if line.strip()]
    if not urls:
        console.print("[bold red]No URLs found in the provided file.[/bold red]")
        raise typer.Exit(1)

    console.print(f"[bold green]Starting batch job for {len(urls)} URLs...[/bold green]\n")
    for idx, url in enumerate(urls, 1):
        console.print(f"[bold magenta]👉 Processing {idx}/{len(urls)}:[/bold magenta] {url}")
        process_url(url)

@app.command()
def watch(poll_interval: int = typer.Option(2, help="Clipboard polling interval in seconds")):
    """Watch the clipboard and automatically process copied Instagram Reel links."""
    console.print(f"[bold cyan]👀 Watching clipboard for Instagram links (interval: {poll_interval}s)...[/bold cyan]")
    console.print("Press Ctrl+C to stop.\n")

    recent_clipboard = ""

    try:
        while True:
            current_clipboard = pyperclip.paste().strip()

            if current_clipboard != recent_clipboard:
                recent_clipboard = current_clipboard
                if is_instagram_reel_url(current_clipboard):
                    console.print(f"\n[bold green]Link detected in clipboard:[/bold green] {current_clipboard}")
                    process_url(current_clipboard)
                    console.print(f"[bold cyan]👀 Resume watching...[/bold cyan]")

            time.sleep(poll_interval)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Clipboard watcher stopped.[/bold yellow]")

if __name__ == "__main__":
    app()
