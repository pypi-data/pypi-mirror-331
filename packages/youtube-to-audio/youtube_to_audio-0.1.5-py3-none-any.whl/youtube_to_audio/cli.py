import click
from youtube_to_audio.downloader import YouTubeDownloader

@click.command()
@click.option("--url", required=True, help="YouTube video or playlist URL")
@click.option("--format", "audio_format", type=click.Choice(["mp3", "wav", "flac", "aac", "ogg", "m4a", "opus"]), default="mp3", help="Audio format (default: mp3)")
@click.option("--output_name", type=str, default=None, help="Custom output file name (only for single videos)")
@click.option("--playlist_name", type=str, default=None, help="Custom folder name for playlist downloads")
def main(url, audio_format, output_name, playlist_name):

    click.secho("🚀 Download Started! Please wait...", fg="green")

    downloader = YouTubeDownloader(audio_format, output_name, playlist_name)

    try:
        message = downloader.download_audio(url)
        click.secho(message, fg="green")
    except Exception as e:
        click.secho(f"❌ Error: {e}", fg="red", err=True)

if __name__ == "__main__":
    main()