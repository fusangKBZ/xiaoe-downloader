import urllib.request as R, re, sys
u = sys.argv[1]
h = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://appvvutermf4498.pc.xiaoe-tech.com/'}
d = R.urlopen(R.Request(u, headers=h), timeout=10).read().decode('utf-8')
k = re.search(r'URI="([^"]+)"', d)
s = [l.strip() for l in d.split('\n') if l.strip() and not l.startswith('#')]
print(f'KEY={k.group(1) if k else "NONE"}')
print(f'SEGS={len(s)}')
