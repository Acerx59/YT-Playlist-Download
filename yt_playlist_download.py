import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Player clients to try in order if a 403 occurs (None = yt-dlp default)
CLIENT_FALLBACKS = [None, "tv", "web_safari", "mweb", "android_vr"]


def ytdlp_base() -> list[str]:
    return [sys.executable, "-m", "yt_dlp"]


def ensure_ytdlp(update: bool):
    """Install or upgrade yt-dlp."""
    try:
        import yt_dlp  # noqa: F401
        installed = True
    except ImportError:
        installed = False

    if not installed or update:
        print("Installing/upgrading yt-dlp...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp[default]"]
        )
        print("yt-dlp is up to date.\n")


def check_environment():
    if shutil.which("ffmpeg") is None:
        print("⚠️  ffmpeg not found. Merging video+audio, mp3 conversion and thumbnail "
              "embedding need it. Install: https://ffmpeg.org/download.html\n")
    if shutil.which("deno") is None and shutil.which("node") is None:
        print("⚠️  No JavaScript runtime found (deno or node). Recent YouTube downloads "
              "often fail with 403 without one. Install Deno (https://deno.com) or Node.js.\n")


def build_command(url: str, args: argparse.Namespace, client: str | None) -> list[str]:
    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = ytdlp_base()

    # Format / quality
    if args.format == "audio":
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
    else:
        q = args.quality
        cmd += [
            "-f", f"bestvideo[height<={q}]+bestaudio/best[height<={q}]/best",
            "--merge-output-format", "mp4",
        ]

    # Playlist range
    if args.start:
        cmd += ["--playlist-start", str(args.start)]
    if args.end:
        cmd += ["--playlist-end", str(args.end)]

    # Output template: playlist folder + index only when it's actually a playlist
    template = str(
        output_dir
        / "%(playlist_title|)s"
        / "%(playlist_index&{} - |)s%(title)s.%(ext)s"
    )
    cmd += ["-o", template]

    cmd += [
        "--embed-thumbnail",
        "--add-metadata",
        "--no-overwrites",
        "--ignore-errors",
        "--progress",
        "--console-title",
        "--retries", "10",
        "--fragment-retries", "10",
        "--sleep-requests", "1",
    ]

    if client:
        cmd += ["--extractor-args", f"youtube:player_client={client}"]

    # Auth: browser cookies take priority over a cookies file
    if args.browser:
        cmd += ["--cookies-from-browser", args.browser]
    elif args.cookies:
        cmd += ["--cookies", args.cookies]

    if args.proxy:
        cmd += ["--proxy", args.proxy]

    if args.concurrent:
        cmd += ["--concurrent-fragments", str(args.concurrent)]

    cmd.append(url)
    return cmd


def main():
    parser = argparse.ArgumentParser(
        description="Download a YouTube playlist or video with yt-dlp (403-resilient)."
    )
    parser.add_argument("url", help="YouTube playlist or video URL")
    parser.add_argument("--output", "-o", default="./downloads", help="Destination folder")
    parser.add_argument("--format", "-f", choices=["video", "audio"], default="video")
    parser.add_argument("--quality", "-q", type=int, default=1080, help="Max video height")
    parser.add_argument("--start", type=int, default=None, help="Playlist start (1-indexed)")
    parser.add_argument("--end", type=int, default=None, help="Playlist end (inclusive)")
    parser.add_argument("--cookies", default=None, help="Path to cookies.txt")
    parser.add_argument("--browser", default=None,
                        help="Use cookies from a browser: chrome, firefox, edge, brave, safari...")
    parser.add_argument("--proxy", default=None, help="Proxy URL, e.g. socks5://127.0.0.1:1080")
    parser.add_argument("--concurrent", type=int, default=4, help="Concurrent fragment downloads")
    parser.add_argument("--no-update", action="store_true", help="Skip yt-dlp upgrade check")
    args = parser.parse_args()

    ensure_ytdlp(update=not args.no_update)
    check_environment()

    print("=" * 60)
    print(f"  URL     : {args.url}")
    print(f"  Format  : {args.format.upper()}")
    if args.format == "video":
        print(f"  Quality : up to {args.quality}p")
    print(f"  Output  : {Path(args.output).expanduser().resolve()}")
    print(f"  Auth    : {args.browser or args.cookies or 'none'}")
    print("=" * 60 + "\n")

    last_code = 1
    try:
        for client in CLIENT_FALLBACKS:
            label = client or "default"
            print(f"▶ Attempt with player client: {label}\n")
            result = subprocess.run(build_command(args.url, args, client))
            if result.returncode == 0:
                print("\n✅  Download complete!")
                return
            last_code = result.returncode
            print(f"\n⚠️  Failed with client '{label}' (code {last_code}). Trying next...\n")
    except KeyboardInterrupt:
        print("\n⏹  Cancelled by user.")
        sys.exit(0)

    print("\n❌  All attempts failed. Try: --browser chrome (while logged into YouTube), "
          "install Deno, or switch networks/VPN.")
    sys.exit(last_code)


if __name__ == "__main__":
    main()
