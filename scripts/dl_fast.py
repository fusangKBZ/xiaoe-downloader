#!/usr/bin/env python3
"""
Download and decrypt a single Xiaoe-Tech course video.
Usage: python dl_fast.py <name> <m3u8_url> <key_url> [cookie_str] [referer]
"""
import urllib.request as R, re, os, sys, time
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from concurrent.futures import ThreadPoolExecutor, as_completed

name = sys.argv[1]
m3u8_url = sys.argv[2]
key_url = sys.argv[3]
cookie_str = sys.argv[4] if len(sys.argv) > 4 else ''
referer = sys.argv[5] if len(sys.argv) > 5 else 'https://appvvutermf4498.pc.xiaoe-tech.com/'

safe = re.sub(r'[<>:"/\\|?*]', '_', name).strip()
out = Path(os.environ.get('TEMP', '/tmp')) / "xiaoe_videos" / f"{safe}.mp4"
if out.exists():
    print(f"SKIP: {safe}")
    sys.exit(0)

ch = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': referer}
kc = ch.copy()
if cookie_str:
    kc['Cookie'] = cookie_str

# 1. Download key
kreq = R.Request(key_url, headers=kc)
key = R.urlopen(kreq, timeout=15).read()
assert len(key) == 16, f"Bad key len {len(key)}"

# 2. Download m3u8 playlist
mreq = R.Request(m3u8_url, headers=ch)
m3u8 = R.urlopen(mreq, timeout=15).read().decode('utf-8')
base = m3u8_url.rsplit('/', 1)[0] + '/'
segs = [l.strip() for l in m3u8.split('\n') if l.strip() and not l.startswith('#')]
print(f"[{safe}] {len(segs)} segs")

# 3. Download and decrypt segments in parallel
def dl_seg(i, seg):
    url = seg if seg.startswith('http') else base + seg
    for _ in range(3):
        try:
            req = R.Request(url, headers=ch)
            data = R.urlopen(req, timeout=15).read()
            cipher = Cipher(algorithms.AES(key), modes.CBC(bytes(16)))
            dec = cipher.decryptor().update(data) + cipher.decryptor().finalize()
            return (i, dec)
        except:
            time.sleep(0.5)
    return (i, None)

results = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(dl_seg, i, s): i for i, s in enumerate(segs)}
    done = 0
    for f in as_completed(futs):
        i, data = f.result()
        if data:
            results[i] = data
        done += 1
        if done % 200 == 0:
            print(f"  [{done}/{len(segs)}]")

if not results:
    print(f"FAIL: {safe} (no valid segments)")
    sys.exit(1)

# 4. Write merged MP4
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, 'wb') as f:
    for i in sorted(results.keys()):
        f.write(results[i])

mb = os.path.getsize(out) / 1048576
print(f"DONE: {safe}.mp4 ({mb:.1f} MB)")
