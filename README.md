# YT-Playlist-Download

python path\yt_playlist_download.py 
python yt_playlist_download.py "YOUR_URL" --output "E:\Downloads\YouTube



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
