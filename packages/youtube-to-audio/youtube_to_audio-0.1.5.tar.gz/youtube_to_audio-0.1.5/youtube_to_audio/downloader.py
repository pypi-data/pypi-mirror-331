import yt_dlp

class YouTubeDownloader:
    SUPPORTED_FORMATS = ["mp3", "wav", "flac", "aac", "ogg", "m4a", "opus"]

    def __init__(self, audio_format: str = "mp3", output_name: str = None, playlist_name: str = None):
        if audio_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Invalid format! Choose between {', '.join(self.SUPPORTED_FORMATS)}.")
        self.audio_format = audio_format
        self.output_name = output_name
        self.playlist_name = playlist_name

    def download_audio(self, youtube_url: str):

        is_playlist = "playlist?" in youtube_url.lower()

        if not is_playlist:
            output_template = f"{self.output_name}.%(ext)s" if self.output_name else "%(title)s.%(ext)s"
        
        else:
            playlist_folder = self.playlist_name if self.playlist_name else "%(playlist_title)s"
            output_template = f"{playlist_folder}/%(title)s.%(ext)s"

        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': self.audio_format,
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.audio_format,
            }],
            'quiet': True,
            'noprogress': True,
            'no_warnings': True,
            'yes_playlist': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

            if is_playlist:
                return f"✅ Playlist download complete! Saved in folder: '{self.playlist_name or 'playlist title'}'."
            else:
                return f"✅ Download complete! Saved as '{self.output_name or 'video title'}.{self.audio_format}'."
                
        except Exception as e:
            raise RuntimeError(f"❌ Error downloading audio: {e}")
