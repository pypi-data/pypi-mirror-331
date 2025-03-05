import os
import pytest
import json
import subprocess
from pathlib import Path
import yt_dlp
from ytdlphelper.cli import get_format_table, find_best_format, main
from typer.testing import CliRunner

TEST_VIDEO_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # First YouTube video ever

def has_ffprobe():
    """Check if ffprobe is available"""
    try:
        subprocess.run(['ffprobe', '-version'], capture_output=True)
        return True
    except FileNotFoundError:
        return False

def get_media_info(filepath):
    """Get media file information using ffprobe"""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        filepath
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

@pytest.fixture
def video_formats():
    """Fetch available formats for the test video"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(TEST_VIDEO_URL, download=False)
        return info.get('formats', [])

def test_format_table_examples(video_formats):
    """Test that format table shows real examples from available formats"""
    format_id = get_format_table(video_formats)
    assert format_id is None  # Since we don't provide input in test
    
    # Verify that the best formats were selected correctly
    best_format = find_best_format(video_formats)
    assert best_format is not None
    
    # If it's a combined format, verify it's h.264+AAC where possible
    if '+' not in best_format['format_id']:
        fmt = next(f for f in video_formats if f['format_id'] == best_format['format_id'])
        if fmt.get('vcodec', '').startswith('avc1'):
            assert fmt.get('ext') == 'mp4'
        if fmt.get('acodec', '').startswith('mp4a'):
            assert 'AAC' in fmt.get('acodec', '').upper()
    else:
        # For separate streams, verify both video and audio
        video_id, audio_id = best_format['format_id'].split('+')
        video_fmt = next(f for f in video_formats if f['format_id'] == video_id)
        audio_fmt = next(f for f in video_formats if f['format_id'] == audio_id)
        
        # Check video format
        if video_fmt.get('vcodec', '').startswith('avc1'):
            assert video_fmt.get('ext') == 'mp4'
        
        # Check audio format
        if audio_fmt.get('acodec', '').startswith('mp4a'):
            assert 'AAC' in audio_fmt.get('acodec', '').upper()

@pytest.mark.skipif(not has_ffprobe(), reason="ffprobe not available")
def test_download_and_verify(tmp_path):
    """Test downloading video and verify format with ffprobe"""
    runner = CliRunner()
    
    # Create temporary directory for download
    os.chdir(tmp_path)
    
    # Download video with best format
    result = runner.invoke(main, [TEST_VIDEO_URL])
    assert result.exit_code == 0
    
    # Find downloaded file
    video_file = next(tmp_path.glob('*.mp4'))
    assert video_file.exists()
    
    # Get media info
    media_info = get_media_info(str(video_file))
    
    # Verify container format
    assert media_info['format']['format_name'] == 'mov,mp4,m4a,3gp,3g2,mj2'
    
    # Verify streams
    streams = media_info['streams']
    video_stream = next((s for s in streams if s['codec_type'] == 'video'), None)
    audio_stream = next((s for s in streams if s['codec_type'] == 'audio'), None)
    
    assert video_stream is not None
    assert audio_stream is not None
    
    # Verify video codec (should be h.264)
    assert video_stream['codec_name'] in ['h264', 'avc1']
    
    # Verify audio codec (should be AAC)
    assert audio_stream['codec_name'] in ['aac', 'mp4a']

def test_format_selection(video_formats):
    """Test that format selection works correctly"""
    # Test automatic format selection
    best_format = find_best_format(video_formats)
    assert best_format is not None
    
    # Verify the format exists
    if '+' in best_format['format_id']:
        video_id, audio_id = best_format['format_id'].split('+')
        assert any(f['format_id'] == video_id for f in video_formats)
        assert any(f['format_id'] == audio_id for f in video_formats)
    else:
        assert any(f['format_id'] == best_format['format_id'] for f in video_formats) 