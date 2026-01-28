# Batch Audio Processor

A Python program for batch processing audio files with the following transformations:
- Convert sample rate to 48kHz
- Convert to 24-bit depth
- Convert to mono
- Normalize using AUFS (Average Unit Full Scale) / LUFS

## Requirements

- Python 3.7 or higher
- **FFmpeg (REQUIRED)** - Needed to load and process most audio formats (FLAC, MP3, M4A, etc.) and for 24-bit export

### Installing FFmpeg

**Windows:**
- Download from https://ffmpeg.org/download.html
- Extract and add to PATH, or
- Use chocolatey: `choco install ffmpeg`

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure FFmpeg is installed and accessible in your PATH.

## Usage

### GUI Mode (Recommended)

Launch the graphical user interface:
```bash
python batch_audio_processor_gui.py
```

The GUI provides:
- Easy directory selection with browse buttons
- Real-time progress bar
- Processing log with detailed information
- Results summary
- Cancel processing option

### Command Line Mode

#### Basic Usage

Process all audio files in a directory:
```bash
python batch_audio_processor.py <input_directory>
```

Processed files will be saved to `<input_directory>/processed/` by default.

#### Specify Output Directory

```bash
python batch_audio_processor.py <input_directory> <output_directory>
```

#### Customize Target LUFS

The default target LUFS is -23.0 (common broadcast standard). You can change it:
```bash
python batch_audio_processor.py <input_directory> <output_directory> --target-lufs -16.0
```

#### Examples

```bash
# Process files in current directory
python batch_audio_processor.py .

# Process files and save to specific output directory
python batch_audio_processor.py ./music ./processed_music

# Process with custom LUFS target
python batch_audio_processor.py ./music ./processed_music --target-lufs -20.0
```

## Supported Audio Formats

- MP3
- WAV
- FLAC
- AAC
- OGG
- M4A
- WMA
- AIFF
- AU

## How It Works

1. **Mono Conversion**: Converts stereo/multi-channel audio to mono
2. **Sample Rate Conversion**: Resamples audio to 48kHz
3. **AUFS Normalization**: Normalizes audio using Average Unit Full Scale (LUFS-based)
4. **24-bit Export**: Exports audio with 24-bit depth using FFmpeg

## Troubleshooting

### "No module named pyaudioop" or "No module named audioop"

This error occurs on Python 3.13+ because the `audioop` module was removed from the standard library. Install the backport:

```bash
pip install audioop-lts
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

### FFmpeg Not Found / "The system cannot find the file specified"

**FFmpeg is REQUIRED** for this program to work. If you see errors about FFmpeg not being found:

1. **Install FFmpeg:**
   - **Windows**: Download from https://ffmpeg.org/download.html or use `choco install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`

2. **Add FFmpeg to PATH:**
   - **Windows**: Add the FFmpeg `bin` folder to your system PATH environment variable
   - Restart your terminal/IDE after adding to PATH

3. **Verify installation:**
   ```bash
   ffmpeg -version
   ```
   If this command works, FFmpeg is properly installed.

**Note**: Without FFmpeg, the program cannot process FLAC, MP3, M4A, and most other audio formats. FFmpeg is used both for loading files and for exporting 24-bit audio.

## Notes

- The program preserves the directory structure of the input files
- The program preserves the original file extension (e.g., .flac files remain .flac, .mp3 files remain .mp3)
- **Metadata is preserved**: All tags (title, artist, album, genre, year, track number, etc.) and cover art are maintained
- If FFmpeg is not available, the program will fall back to pydub's export (may not guarantee exact 24-bit depth)
- Files are exported in their original format with the specified audio settings (48kHz, 24-bit, mono, normalized)

