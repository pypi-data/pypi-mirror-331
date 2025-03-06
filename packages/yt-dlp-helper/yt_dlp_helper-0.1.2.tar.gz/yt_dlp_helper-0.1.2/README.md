# yt-dlp-helper

A beautiful command-line wrapper for yt-dlp with a rich interface.

## Installation

```bash
pip install yt-dlp-helper
```

To upgrade to the latest version:
```bash
pip install --upgrade yt-dlp-helper
```

## Usage

Download a video with best quality (h.264/mp4, up to 1080p):
```bash
download "https://www.youtube.com/watch?v=..."
```

Interactive format selection with automatic conversion option:
```bash
download "https://www.youtube.com/watch?v=..." --ask-format
# or
download "https://www.youtube.com/watch?v=..." -a
```

Manual format selection:
```bash
download "https://www.youtube.com/watch?v=..." --format "bestvideo[height<=1080]+bestaudio/best"
# or
download "https://www.youtube.com/watch?v=..." -f "bestvideo[height<=1080]+bestaudio/best"
```

## Features

- Beautiful progress bars and status indicators
- Smart format selection prioritizing h.264/mp4 formats
- Interactive format selection with detailed information
- Automatic format conversion to h.264/mp4 when needed
- Rich CLI interface with helpful error messages

## Format Selection

The tool prioritizes formats in the following order:
1. Best h.264/mp4 format up to 1080p
2. Best separate h.264 video + audio combination
3. Other formats with optional conversion to h.264/mp4

When using `--ask-format` or `-a`, you'll see a detailed table of available formats with:
- Resolution and FPS
- File size
- Video and audio codecs
- Bitrate information
- Format-specific notes

Formats are organized into three categories:
1. Combined formats (video + audio)
2. Video-only formats
3. Audio-only formats

You can select:
- A single format ID for combined formats
- Two format IDs (e.g., "137+251") to combine video and audio
- Non-h.264/mp4 formats with automatic conversion option

## License

MIT

## Author

Isaac Gutekunst 