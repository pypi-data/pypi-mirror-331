"""
CLI implementation for the download package
"""
import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import requests
from typing import Optional, Dict, List, Tuple
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.markup import escape
from rich.text import Text
from rich.live import Live
import yt_dlp

__version__ = "0.1.0"  # Update this with your actual version

app = typer.Typer(
    help="A beautiful wrapper for yt-dlp",
    add_completion=False,
)

# Single console instance for the entire application
console = Console()

# Global progress instance
progress = Progress(
    SpinnerColumn(),
    TextColumn("[bold blue]{task.description}"),
    BarColumn(bar_width=40),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    "[bold blue]{task.completed}/{task.total}",
    "•",
    TimeRemainingColumn(),
    console=console,
    transient=False,
    expand=True,
    refresh_per_second=10
)

def check_for_updates():
    """Check PyPI for updates, but only once per day"""
    try:
        # Create config directory if it doesn't exist
        config_dir = Path.home() / ".yt-dlp-helper"
        config_dir.mkdir(exist_ok=True)
        
        data_file = config_dir / "data.json"
        data = {}
        
        # Load existing data
        if data_file.exists():
            try:
                with open(data_file) as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                pass

        # Check if we need to check for updates
        last_check = data.get('last_update_check')
        if last_check:
            last_check = datetime.fromisoformat(last_check)
            if datetime.now() - last_check < timedelta(days=1):
                return

        # Check PyPI for the latest version
        response = requests.get("https://pypi.org/pypi/yt-dlp-helper/json", timeout=2)
        if response.status_code == 200:
            latest_version = response.json()['info']['version']
            if latest_version > __version__:
                console.print(f"[yellow]A new version of yt-dlp-helper is available: {latest_version}[/yellow]")
                console.print("[yellow]Run 'pip install --upgrade yt-dlp-helper' to update[/yellow]")

        # Update last check time
        data['last_update_check'] = datetime.now().isoformat()
        with open(data_file, 'w') as f:
            json.dump(data, f)

    except Exception:
        # Silently ignore any errors during update check
        pass

def format_filesize(bytes: Optional[float]) -> str:
    if not bytes:
        return "N/A"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024
    return f"{bytes:.1f}TB"

def get_format_table(formats: List[Dict]) -> Optional[str]:
    # First clear the screen to ensure clean state
    console.clear()
    
    table = Table(
        "ID", "Extension", "Resolution", "Filesize", "Video Codec",
        "Audio Codec", "Note",
        title="Available Formats",
        show_lines=True,
        title_style="bold blue",
        header_style="bold cyan",
        border_style="blue",
        expand=True,
        show_footer=False,
    )

    # Group and sort formats
    video_formats = []
    audio_formats = []
    combined_formats = []

    for f in formats:
        vcodec = f.get('vcodec', 'none')
        acodec = f.get('acodec', 'none')
        
        if vcodec != 'none' and acodec != 'none':
            combined_formats.append(f)
        elif vcodec != 'none':
            video_formats.append(f)
        elif acodec != 'none':
            audio_formats.append(f)

    # Sort formats by quality
    video_formats.sort(key=lambda x: (x.get('height', 0) or 0, x.get('tbr', 0) or 0), reverse=True)
    audio_formats.sort(key=lambda x: x.get('tbr', 0) or 0, reverse=True)
    combined_formats.sort(key=lambda x: (x.get('height', 0) or 0, x.get('tbr', 0) or 0), reverse=True)

    # Add formats to table
    if combined_formats:
        table.add_row("[bold cyan]Combined Formats[/bold cyan]", "", "", "", "", "", "")
        for f in combined_formats:
            add_format_row(table, f)

    if video_formats:
        table.add_row("[bold cyan]Video-only Formats[/bold cyan]", "", "", "", "", "", "")
        for f in video_formats:
            add_format_row(table, f)

    if audio_formats:
        table.add_row("[bold cyan]Audio-only Formats[/bold cyan]", "", "", "", "", "", "")
        for f in audio_formats:
            add_format_row(table, f)

    # Print table and instructions
    console.print(table)
    console.print()
    
    # Find best examples from available formats
    best_combined = None
    best_video = None
    best_audio = None
    
    # Find best combined format (prefer h.264/mp4)
    for f in combined_formats:
        if (f.get('vcodec', '').startswith('avc1') and 
            f.get('acodec', '').startswith('mp4a') and
            f.get('ext') == 'mp4'):
            best_combined = f
            break
    if not best_combined and combined_formats:
        best_combined = combined_formats[0]
        
    # Find best video format (prefer h.264/mp4 1080p)
    for f in video_formats:
        if (f.get('vcodec', '').startswith('avc1') and
            f.get('ext') == 'mp4' and
            f.get('height', 0) >= 720):
            best_video = f
            break
    if not best_video and video_formats:
        best_video = video_formats[0]
        
    # Find best audio format (prefer AAC)
    for f in audio_formats:
        if f.get('acodec', '').startswith('mp4a'):
            best_audio = f
            break
    if not best_audio and audio_formats:
        best_audio = audio_formats[0]
    
    # Create instructions text with real examples
    instructions = Text()
    instructions.append("Format Selection Instructions:", style="bold blue")
    instructions.append("\n• Enter a single format ID for combined formats")
    instructions.append("\n• Or combine video and audio formats with '+' (e.g., ", style="")
    if best_video and best_audio:
        instructions.append(f"{best_video['format_id']}+{best_audio['format_id']}", style="cyan")
    else:
        instructions.append("137+251", style="cyan")  # Fallback example
    instructions.append(")")
    instructions.append("\n• Type ", style="")
    instructions.append("q", style="cyan")
    instructions.append(" to quit")
    instructions.append("\n\nExamples:", style="bold blue")
    
    if best_combined:
        instructions.append("\n• ", style="")
        instructions.append(best_combined['format_id'], style="cyan")
        instructions.append(f" - Download combined format {best_combined['format_id']} ({best_combined.get('format_note', '')} {best_combined.get('ext', '')})")
    
    if best_video and best_audio:
        instructions.append("\n• ", style="")
        instructions.append(f"{best_video['format_id']}+{best_audio['format_id']}", style="cyan")
        instructions.append(f" - Combine format {best_video['format_id']} ({best_video.get('format_note', '')} video) with {best_audio['format_id']} ({best_audio.get('format_note', '')} audio)")
    
    console.print(instructions)
    console.print()  # Add extra newline for spacing
    
    try:
        # Use Prompt.ask for consistent styling
        format_id = Prompt.ask("[bold blue]Enter format ID", show_default=False)
        if not format_id or format_id.lower() == 'q':
            return None

        # Validate format ID
        format_ids = format_id.split('+')
        valid_format_ids = [f['format_id'] for f in formats]
        for fmt_id in format_ids:
            fmt_id = fmt_id.strip()
            if fmt_id not in valid_format_ids:
                console.print(f"[red]Error:[/red] Invalid format ID '{fmt_id}'")
                return None

        return format_id
    except (KeyboardInterrupt, EOFError):
        console.print()
        return None

def add_format_row(table: Table, f: Dict):
    resolution = f"{f.get('width', '')}x{f.get('height', '')}"
    if f.get('fps'):
        resolution += f" {f.get('fps')}fps"
    elif f.get('acodec', 'none') != 'none' and f.get('vcodec', 'none') == 'none':
        resolution = "audio only"

    table.add_row(
        f.get('format_id', 'N/A'),
        f.get('ext', 'N/A'),
        resolution,
        f.get('filesize_str', 'N/A'),
        f.get('vcodec', 'none'),
        f.get('acodec', 'none'),
        f"{f.get('format_note', '')}, {f.get('tbr', '')}Kbps".strip(', ')
    )

def find_best_format(formats: List[Dict]) -> Optional[Dict]:
    # First try to find a combined format with h.264 1080p and AAC audio
    for f in formats:
        if (f.get('vcodec', '').startswith('avc1') and
            f.get('ext') == 'mp4' and
            f.get('height', 0) == 1080 and
            f.get('acodec', 'none') != 'none' and
            f.get('acodec', '').startswith('mp4a')):  # mp4a is AAC
            return f

    # If no combined format found, look for best video and audio separately
    best_video = None
    best_audio = None

    # Find best h.264 1080p video
    for f in formats:
        if (f.get('vcodec', '').startswith('avc1') and
            f.get('ext') == 'mp4' and
            f.get('height', 0) == 1080 and
            f.get('acodec', 'none') == 'none'):
            if not best_video or f.get('tbr', 0) > best_video.get('tbr', 0):
                best_video = f

    # Find best AAC audio
    for f in formats:
        if (f.get('acodec', 'none') != 'none' and 
            f.get('vcodec', 'none') == 'none'):
            # Prefer AAC audio
            is_aac = f.get('acodec', '').startswith('mp4a')
            current_is_aac = best_audio and best_audio.get('acodec', '').startswith('mp4a')
            
            if not best_audio or (is_aac and not current_is_aac) or (
                (is_aac == current_is_aac) and f.get('tbr', 0) > best_audio.get('tbr', 0)
            ):
                best_audio = f

    if best_video and best_audio:
        return {'format_id': f"{best_video['format_id']}+{best_audio['format_id']}"}

    return None

def select_format(url: str) -> Optional[Tuple[str, Dict]]:
    """Get format information and let user select one"""
    task_id = progress.add_task("[bold blue]Fetching video information...", total=None)
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            progress.update(task_id, description="[bold green]✓ Video information fetched!")
    except Exception as e:
        progress.update(task_id, description=f"[bold red]✗ Error: {str(e)}")
        return None
    finally:
        progress.remove_task(task_id)
    
    if not formats:
        console.print("[yellow]Warning:[/yellow] No formats found")
        return None
    
    format_id = get_format_table(formats)
    if not format_id:
        return None
    
    selected_format = next(
        (f for f in formats if f['format_id'] == format_id.strip()),
        None
    )
            
    return format_id, selected_format

class DownloadProgress:
    def __init__(self):
        self.error = None
        self.completed = False
        self.task = None
        self.current_stage = None
        # Track both streams
        self.streams = {}
        self.total_bytes = 0
        self.downloaded_bytes = 0
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.task:
            progress.remove_task(self.task)

    def download_hook(self, d):
        status = d['status']
        
        if status == 'error':
            self.error = d.get('error', 'Unknown error')
            if self.task:
                progress.update(self.task, description=f"[bold red]Error: {escape(str(self.error))}")
            return

        if status == 'downloading':
            # Get unique stream identifier
            stream_id = d.get('info_dict', {}).get('format_id', 'unknown')
            
            if not self.task or self.current_stage != 'downloading':
                if self.task:
                    progress.remove_task(self.task)
                self.streams.clear()
                self.total_bytes = 0
                self.downloaded_bytes = 0
                self.task = progress.add_task(
                    "[bold blue]Starting download...",
                    total=100,  # Use percentage for combined progress
                )
                self.current_stage = 'downloading'
            
            # Update stream info
            if stream_id not in self.streams:
                # Get total bytes, preferring total_bytes over total_bytes_estimate
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                self.streams[stream_id] = {
                    'total': total,
                    'downloaded': 0,
                    'filename': d.get('filename', ''),
                    'speed': 0
                }
            
            # Update stream progress and total bytes if we get a better estimate
            current_stream = self.streams[stream_id]
            new_total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if new_total and new_total > current_stream['total']:
                old_total = current_stream['total']
                current_stream['total'] = new_total
                # Update overall total
                self.total_bytes = self.total_bytes - old_total + new_total
            
            # Update downloaded bytes
            new_downloaded = d.get('downloaded_bytes', 0)
            current_stream.update({
                'downloaded': new_downloaded,
                'speed': d.get('speed', 0)
            })
            
            # Calculate combined progress
            self.downloaded_bytes = sum(s['downloaded'] for s in self.streams.values())
            total_speed = sum(s['speed'] for s in self.streams.values() if s['speed'] is not None)
            
            # Create description
            if len(self.streams) > 1:
                description = "[bold blue]Downloading video and audio..."
            else:
                description = f"[bold blue]Downloading {escape(d['filename'])}..."
            
            if total_speed > 0:
                description += f" ({format_filesize(total_speed)}/s)"
            
            # Update progress as percentage
            if self.total_bytes > 0:
                percentage = (self.downloaded_bytes / self.total_bytes) * 100
                # Only show 100% if we're really done
                if percentage > 99.9 and self.downloaded_bytes < self.total_bytes:
                    percentage = 99.9
                progress.update(
                    self.task,
                    completed=percentage,
                    description=description
                )
            else:
                # If we don't have a total size, show the downloaded amount
                description += f" ({format_filesize(self.downloaded_bytes)} downloaded)"
                progress.update(self.task, description=description)
        
        elif status == 'finished':
            # Don't complete the task until all streams are done
            stream_id = d.get('info_dict', {}).get('format_id', 'unknown')
            if stream_id in self.streams:
                del self.streams[stream_id]
            
            if not self.streams:  # All streams completed
                if self.task:
                    progress.update(self.task, description="[bold green]Download completed!", completed=100)
                    progress.remove_task(self.task)
                    self.task = None
                self.completed = True
                console.print(f"[green]✓[/green] Download completed!")
        
        elif status == 'processing':
            if not self.task or self.current_stage != 'processing':
                if self.task:
                    progress.remove_task(self.task)
                self.task = progress.add_task(
                    "[bold yellow]Processing video...",
                    total=None
                )
                self.current_stage = 'processing'
            
            status_str = d.get('status_str', 'Converting...')
            progress.update(
                self.task,
                description=f"[bold yellow]Processing: {escape(str(status_str))}"
            )

def get_yt_dlp_opts(progress: Progress, post_process: bool = False) -> Tuple[Dict, DownloadProgress]:
    download_progress = DownloadProgress()
    
    opts = {
        'format': None,  # Will be set later
        'progress_hooks': [download_progress.download_hook],
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',  # Always merge to mp4
    }
    
    if post_process:
        opts.update({
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        })
    
    return opts, download_progress

def make_json_serializable(obj):
    """Convert an object to a JSON-serializable format"""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, set):
        return [make_json_serializable(item) for item in obj]
    else:
        return str(obj)

@app.command()
def main(
    url: str, 
    ask_format: bool = False,
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show verbose output for debugging")
):
    # Check for updates
    check_for_updates()

    try:
        # First, fetch metadata with its own progress context
        with progress:
            task_id = progress.add_task("[bold blue]Fetching video information...", total=None)
            try:
                ydl_opts = {
                    'quiet': not verbose,
                    'no_warnings': not verbose,
                    'noprogress': True,
                    'logger': None if not verbose else None  # TODO: Add custom logger for verbose mode
                }
                
                if verbose:
                    console.print("[bold blue]Debug:[/bold blue] Fetching video metadata...")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    formats = info.get('formats', [])
                    if not formats:
                        console.print("[red]Error:[/red] No formats available")
                        raise typer.Exit(code=1)
                    progress.update(task_id, description="[bold green]✓ Video information fetched!")
            except Exception as e:
                progress.update(task_id, description=f"[bold red]✗ Error: {str(e)}")
                raise
            finally:
                progress.remove_task(task_id)

        # Then handle format selection without any progress context
        if ask_format:
            format_id = get_format_table(formats)
            if not format_id:
                return
            ydl_opts['format'] = format_id
            
            # Echo the selection
            format_ids = format_id.split('+')
            if len(format_ids) == 1:
                fmt = next((f for f in formats if f['format_id'] == format_ids[0].strip()), None)
                if fmt:
                    console.print(f"\n[green]Selected format:[/green] {fmt.get('format_note', '')} ({fmt.get('ext', '')})")
            else:
                video_fmt = next((f for f in formats if f['format_id'] == format_ids[0].strip()), None)
                audio_fmt = next((f for f in formats if f['format_id'] == format_ids[1].strip()), None)
                if video_fmt and audio_fmt:
                    console.print(f"\n[green]Selected combination:[/green]")
                    console.print(f"• Video: {video_fmt.get('format_note', '')} ({video_fmt.get('ext', '')})")
                    console.print(f"• Audio: {audio_fmt.get('format_note', '')} ({audio_fmt.get('ext', '')})")
        else:
            best_format = find_best_format(formats)
            if not best_format:
                console.print("[red]Error:[/red] No suitable format found")
                raise typer.Exit(code=1)
            ydl_opts['format'] = best_format['format_id']

        # Check if any selected format needs conversion
        selected_formats = ydl_opts['format'].split('+')
        needs_video_conversion = False
        needs_audio_conversion = False
        is_combined_format = len(selected_formats) == 1

        for fmt in formats:
            if fmt['format_id'] in selected_formats:
                if 'vcodec' in fmt and fmt['vcodec'] != 'none':
                    if not fmt['vcodec'].startswith('avc1') or fmt['ext'] != 'mp4':
                        needs_video_conversion = True
                if 'acodec' in fmt and fmt['acodec'] != 'none':
                    if not fmt['acodec'].startswith('mp4a'):
                        needs_audio_conversion = True

        # Always set merge format for separate streams
        if not is_combined_format:
            ydl_opts['merge_output_format'] = 'mp4'
            ydl_opts['keepvideo'] = True
            # Don't ask about conversion for separate streams, just ensure proper merging
            if needs_video_conversion or needs_audio_conversion:
                ydl_opts['postprocessors'] = []
                if needs_video_conversion:
                    ydl_opts['postprocessors'].append({
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                        'keepvideo': True,
                    })
                if needs_audio_conversion:
                    ydl_opts['postprocessors'].append({
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'aac',
                        'preferredquality': '0',
                        'keepvideo': True,
                    })
        elif needs_video_conversion or needs_audio_conversion:
            # Only ask about conversion for combined formats
            convert = Confirm.ask(
                "Selected format is not h.264/mp4 with AAC audio. Convert after download?",
                default=True
            )
            if convert:
                ydl_opts['postprocessors'] = []
                if needs_video_conversion:
                    ydl_opts['postprocessors'].append({
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                        'keepvideo': True,
                    })
                if needs_audio_conversion:
                    ydl_opts['postprocessors'].append({
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'aac',
                        'preferredquality': '0',
                        'keepvideo': True,
                    })

        # Finally, handle the download with its own progress context
        ydl_opts.update({
            'quiet': not verbose,
            'no_warnings': not verbose,
            'noprogress': True,
            'logger': None,
            'compat_opts': [],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4556.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate'
            },
            'forceprint': {},
            'print_to_file': {},
            'outtmpl': {
                'default': '%(title)s [%(id)s].%(ext)s',
                'chapter': '%(title)s - %(section_number)03d %(section_title)s [%(id)s].%(ext)s'
            },
            'format': ydl_opts['format'],
            'merge_output_format': 'mp4',
            'keepvideo': True,
        })

        with progress:
            with DownloadProgress() as download_progress:
                ydl_opts['progress_hooks'] = [download_progress.download_hook]
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        # Show what we're going to do
                        if len(selected_formats) > 1:
                            console.print("\n[bold blue]Download plan:[/bold blue]")
                            if verbose:
                                console.print(f"[dim]Debug: Using options:[/dim]")
                                console.print(f"[dim]{json.dumps(make_json_serializable(ydl_opts), indent=2)}[/dim]")
                            console.print(f"• Downloading video format: {selected_formats[0]}")
                            console.print(f"• Downloading audio format: {selected_formats[1]}")
                            console.print("• Will merge into MP4 after download")
                            if needs_video_conversion:
                                console.print("• Will convert video to H.264")
                            if needs_audio_conversion:
                                console.print("• Will convert audio to AAC")
                        else:
                            console.print("\n[bold blue]Download plan:[/bold blue]")
                            if verbose:
                                console.print(f"[dim]Debug: Using options:[/dim]")
                                console.print(f"[dim]{json.dumps(make_json_serializable(ydl_opts), indent=2)}[/dim]")
                            console.print(f"• Downloading combined format: {selected_formats[0]}")
                            if needs_video_conversion or needs_audio_conversion:
                                if needs_video_conversion:
                                    console.print("• Will convert video to H.264")
                                if needs_audio_conversion:
                                    console.print("• Will convert audio to AAC")
                        console.print()  # Empty line for spacing
                        
                        # Do the download
                        ydl.download([url])
                        
                        # Clean up temporary files
                        if len(selected_formats) > 1:
                            # Get the directory of the output file
                            output_path = ydl.prepare_filename(info)
                            if verbose:
                                console.print(f"[dim]Debug: Output path: {output_path}[/dim]")
                            
                            if not output_path:
                                raise ValueError("Could not determine output path")
                                
                            output_dir = os.path.dirname(output_path)
                            if verbose:
                                console.print(f"[dim]Debug: Output directory: {output_dir}[/dim]")
                            
                            if not output_dir:
                                output_dir = "."
                                if verbose:
                                    console.print("[dim]Debug: Using current directory for cleanup[/dim]")
                            
                            # Look for temporary files
                            for file in os.listdir(output_dir):
                                if verbose:
                                    console.print(f"[dim]Debug: Checking file: {file}[/dim]")
                                if file.endswith('.f'+selected_formats[0]+'.mp4') or \
                                   file.endswith('.f'+selected_formats[1]+'.m4a') or \
                                   file.endswith('.f'+selected_formats[1]+'.webm'):
                                    try:
                                        full_path = os.path.join(output_dir, file)
                                        if verbose:
                                            console.print(f"[dim]Debug: Removing file: {full_path}[/dim]")
                                        os.remove(full_path)
                                        console.print(f"[dim]Cleaned up temporary file: {file}[/dim]")
                                    except OSError as e:
                                        if verbose:
                                            console.print(f"[yellow]Debug: Failed to remove {file}: {str(e)}[/yellow]")
                            
                    except yt_dlp.utils.DownloadError as e:
                        if verbose:
                            console.print(f"[red]Debug: Download error details: {str(e)}[/red]")
                        download_progress.error = str(e)
                    except Exception as e:
                        if verbose:
                            import traceback
                            console.print(f"[red]Debug: Unexpected error:[/red]")
                            console.print(f"[red]{traceback.format_exc()}[/red]")
                        raise

                if download_progress.error:
                    if verbose:
                        console.print(f"[red]Debug: Final error state: {download_progress.error}[/red]")
                    console.print(f"[red]Error:[/red] {download_progress.error}")
                    raise typer.Exit(code=1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Download cancelled[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        if verbose:
            import traceback
            console.print(f"[red]Debug: Full traceback:[/red]")
            console.print(f"[red]{traceback.format_exc()}[/red]")
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app() 