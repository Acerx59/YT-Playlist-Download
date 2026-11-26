# YT-Playlist-Download

python path\yt_playlist_download.py 

python yt_playlist_download.py "YOUR_URL" --output "path"



YouTube Playlist Downloader
Uses yt-dlp to download entire playlists or single videos.

Install dependency:
    pip install yt-dlp
    Install Deno 
        winget install DenoLand.Deno  (Windows)

    Add --no-update only after it works, to avoid re-upgrading on every run

Usage:
python yt_playlist_download.py "PLAYLIST_URL" -q 1080

python yt_playlist_download.py "PLAYLIST_URL" --browser chrome -q 1080
