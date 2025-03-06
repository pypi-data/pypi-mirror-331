# YouTube-to-Audio CLI Tool

A lightweight Python package and command-line interface (CLI) tool that extracts audio from YouTube videos and playlists in multiple formats, such as MP3, WAV, OGG, AAC, and FLAC.

## Features

- Extract audio from YouTube videos or playlists in various formats: MP3, WAV, OGG, AAC, FLAC, M4A, and OPUS.
- Customize the output audio file name.
- By default, names the audio files and playlists after the YouTube video or playlist title.
- Automatically cleans up temporary video files after extraction.

## Installation

To install the package from PyPI, run the following command:

```
pip install youtube-to-audio
```

## Usage

### 1. Download and Extract Audio from a Single Video in the Default Format (MP3)

```
youtube-to-audio --url "https://www.youtube.com/watch?v=WysanSNOjMc"
```

This command extracts the audio in MP3 format and saves it with the same name as the YouTube video title (e.g., `The Video Title.mp3`).

### 2. Extract Audio from a Playlist in MP3 Format

```
youtube-to-audio --url "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgnymQGm0yIxcdzkQsPKwnBD"
```

This command extracts audio from all videos in a playlist and saves each file by default in a folder named after the playlist, using the YouTube video title as the filename (e.g., `Video1.mp3`, `Video2.mp3`, etc.).

### 3. Extract Audio in a Different Format (e.g., WAV)

```
youtube-to-audio --url "https://www.youtube.com/watch?v=WysanSNOjMc" --format wav
```

This command extracts the audio in WAV format and saves it with the YouTube video title (e.g., `Your Video Title.wav`).

### 4. Specify a Custom Audio File Name

```
youtube-to-audio --url "https://www.youtube.com/watch?v=WysanSNOjMc" --format wav --output_name "my_custom_name"
```

This command extracts the audio in WAV format and saves it as `my_custom_name.wav`.

### 5. Extract a Playlist into a Custom Folder

```
youtube-to-audio --url "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgnymQGm0yIxcdzkQsPKwnBD" --playlist_name "MyPlaylist"
```

This saves all extracted audio files inside a folder named `MyPlaylist` instead of using the default playlist title.

---

## Command-Line Options

| Option            | Description                                                      | Required             | Usage Scenario                           |
| ----------------- | ---------------------------------------------------------------- | -------------------- | ---------------------------------------- |
| `--url`           | YouTube video or playlist URL                                    | ✅ Yes               | Required for all cases                   |
| `--format`        | Audio format (`mp3`, `wav`, `flac`, `aac`, `ogg`, `m4a`, `opus`) | ❌ No (default: mp3) | Extracting in a specific format          |
| `--output_name`   | Custom output file name (single videos only)                     | ❌ No                | Naming a single file differently         |
| `--playlist_name` | Custom folder name for playlist downloads                        | ❌ No                | Saving a playlist into a specific folder |

---

## Requirements

This tool requires **FFmpeg** to be installed on your system. If FFmpeg is not found, the tool will not be able to extract audio.

---

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! If you have suggestions or bug fixes, feel free to open a pull request.

---

## Author

Developed by **Jack Tol**  
[GitHub Repository](https://github.com/jack-tol/youtube-to-audio)
