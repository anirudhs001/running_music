
import os
from tqdm import tqdm
from yt_dlp import YoutubeDL
from bpm_detection.bpm_detection import get_bpm 
from ytmusicapi import YTMusic
from collections import defaultdict
import argparse
import json


PLAYLIST_IDS_FILE = "playlist_ids.json"

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'quiet':True,
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
    }],
    'progress_hooks': [my_hook],
}

def search(arg, count=1, download=True, max_duration=300):
    with YoutubeDL(ydl_opts) as ydl:
        res = ydl.extract_info(f"ytsearch{count}:{arg}", download=download)
        info = res['entries']
        info = [i for i in info if i['duration'] <= max_duration]
        filenames = [ydl.prepare_filename(i) for i in info]
        filenames = [f.replace('.webm', '.wav') for f in filenames]

    return filenames, info

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', '-q', type=str, required=True)
    parser.add_argument('--count', '-c', type=int, required=True)
    parser.add_argument('--keep_files', choices=['y', 'n'], default='n')
    args = parser.parse_args()
    keep_files = True if args.keep_files == 'y' else False
    if keep_files:
        print("Keeping files after download")
    else :
        print("deleting files after download")

    with open(PLAYLIST_IDS_FILE, 'r+') as f:
        playlist_ids = json.load(f)
    

    ytmusic = YTMusic('headers_auth.json')
    fnames, info = search(args.query, args.count, True)
    song_lists = defaultdict(list)
    download_bar = tqdm(zip(fnames, info))
    for fname, i in download_bar:
        download_bar.set_description(f"{i['title']}")
        try: 
            b = get_bpm(fname)
            category = int(b - b%10)
            song_lists[category].append(i['title'])
            if keep_files:
                try:
                    os.mkdir(str(category))
                except:
                    pass
                os.rename(fname, f"{category}/{fname}")
            else :
                os.remove(f"./{fname}")
        except:
            pass
    

    #create playlists
    playlist_bar = tqdm(song_lists)
    for cat in playlist_bar:
        try : 
            if f'{cat}' in playlist_ids:
                playlistId = playlist_ids[f"{cat}"]
            else:
                playlistId = ytmusic.create_playlist(f'{cat}-{cat+5}', f'{cat} bpm')
                playlist_ids[f"{cat}"] = playlistId

            for song in song_lists[cat]:
                playlist_bar.set_description(f"{cat}:{song}")
                search_results = ytmusic.search(song)
                ytmusic.add_playlist_items(playlistId, [search_results[0]['videoId']])
        except:
            pass

    with open(PLAYLIST_IDS_FILE, 'w+') as f:
        json.dump(playlist_ids, f)
