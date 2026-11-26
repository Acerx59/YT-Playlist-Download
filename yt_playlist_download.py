YouTube Playlist Downloader
Uses yt-dlp to download entire playlists or single videos.

Install dependency:
    pip install yt-dlp

Usage:
    python yt_playlist_download.py <URL> [options]

Examples:
    python yt_playlist_download.py "https://www.youtube.com/playlist?list=PLxxx"
    python yt_playlist_download.py "https://youtu.be/VIDEO_ID" --format audio
    python yt_playlist_download.py "https://www.youtube.com/playlist?list=PLxxx" --output ~/Music --format audio
    python yt_playlist_download.py "https://www.youtube.com/playlist?list=PLxxx" --quality 720 --start 5 --end 20
"""

import argparse
import subprocess
import sys
import shutil
from pathlib import Path


def check_yt_dlp():
    """Ensure yt-dlp is installed."""
    if shutil.which("yt-dlp") is None:
        print("yt-dlp not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yt-dlp"])
        print("yt-dlp installed successfully.\n")


def build_command(url: str, args: argparse.Namespace) -> list[str]:
    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["yt-dlp"]

    #Format / quality
    if args.format == "audio":
        cmd += [
            "-x",                          # extract audio
            "--audio-format", "mp3",
            "--audio-quality", "0",        # best quality
        ]
    else:
        # Video: prefer specified quality, fall back to best available
        quality = args.quality
        cmd += [
            "-f",
            f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best",
            "--merge-output-format", "mp4",
        ]

    #  Playlist range
    if args.start:
        cmd += ["--playlist-start", str(args.start)]
    if args.end:
        cmd += ["--playlist-end", str(args.end)]

    #  Output template
    # Organise into a sub-folder named after the playlist (or video title).
    template = str(output_dir / "%(playlist_title)s" / "%(playlist_index)s - %(title)s.%(ext)s")
    cmd += ["-o", template]

    # Nice extras
    cmd += [
        "--embed-thumbnail",               # embed album art / video thumbnail
        "--add-metadata",                  # write ID3 / mp4 tags
        "--no-overwrites",                 # skip already-downloaded files
        "--ignore-errors",                 # keep going if one video fails
        "--progress",
        "--console-title",
    ]

    if args.cookies:
        cmd += ["--cookies", args.cookies]

    if args.proxy:
        cmd += ["--proxy", args.proxy]

    if args.concurrent:
        cmd += ["--concurrent-fragments", str(args.concurrent)]

    cmd.append(url)
    return cmd


def main():
    parser = argparse.ArgumentParser(
        description="Download a YouTube playlist or video with yt-dlp.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("url", help="YouTube playlist or video URL")
    parser.add_argument(
        "--output", "-o",
        default="./downloads",
        help="Destination folder (default: ./downloads)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["video", "audio"],
        default="video",
        help="Download as video (mp4) or audio-only (mp3). Default: video",
    )
    parser.add_argument(
        "--quality", "-q",
        type=int,
        default=1080,
        help="Max video height in pixels (e.g. 720, 1080). Default: 1080",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=None,
        help="Start downloading from this playlist position (1-indexed)",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="Stop downloading at this playlist position (inclusive)",
    )
    parser.add_argument(
        "--cookies",
        default=None,
        help="Path to a cookies.txt file (for age-restricted / private videos)",
    )
    parser.add_argument(
        "--proxy",
        default=None,
        help="Proxy URL (e.g. socks5://127.0.0.1:1080)",
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=4,
        help="Number of concurrent fragment downloads (default: 4)",
    )

    args = parser.parse_args()

    check_yt_dlp()

    cmd = build_command(args.url, args)

    print("=" * 60)
    print(f"  URL     : {args.url}")
    print(f"  Format  : {args.format.upper()}")
    if args.format == "video":
        print(f"  Quality : up to {args.quality}p")
    if args.start or args.end:
        print(f"  Range   : {args.start or 'start'} → {args.end or 'end'}")
    print(f"  Output  : {Path(args.output).expanduser().resolve()}")
    print("=" * 60)
    print()

    try:
        subprocess.run(cmd, check=True)
        print("\n✅  Download complete!")
    except subprocess.CalledProcessError as exc:
        print(f"\n❌  yt-dlp exited with code {exc.returncode}.")
        sys.exit(exc.returncode)
    except KeyboardInterrupt:
        print("\n⏹  Cancelled by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
