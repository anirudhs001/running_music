
import os
from tqdm import tqdm
from yt_dlp import YoutubeDL
from bpm_detection.bpm_detection import get_bpm 
import urllib

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

    return info

if __name__ == "__main__":
    info = search("workout amv", 5, False)
    bpms = {}
    for i in tqdm(info):
        fname = f"{i['title']} [{i['id']}].wav"
        # urllib.request.urlretrieve(i['url'], fname)
        try: 
            b = get_bpm(fname)
            bpms[fname] = b
            category = int(b - b%10)
            try:
                os.mkdir(str(category))
            except:
                pass
            os.rename(fname, f"{category}/{fname}")
        except:
            pass
    

