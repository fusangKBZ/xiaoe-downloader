---
name: xiaoe-downloader
description: |
  Download purchased course videos from Xiaoe-Tech (小鹅通) platform in bulk. 
  Handles WeChat QR login, course list extraction, m3u8 URL capture, AES-128-CBC 
  decryption, and multi-threaded TS segment download + merge to MP4.
  Use when the user mentions downloading courses from Xiaoe-Tech/小鹅通, 
  batch downloading purchased videos, 小鹅通课程下载, 下载已购视频, 
  or needs to save online courses locally before they expire.
  MANDATORY TRIGGERS: 小鹅通, xiaoe-tech, xiaoeknow, 下载课程, 
  batch download course videos, 课程视频下载
---

# Xiaoe-Tech Course Video Downloader

Download all purchased course videos from a Xiaoe-Tech (小鹅通) course column page 
to local MP4 files. Automates the entire pipeline: login → course discovery → 
m3u8 extraction → AES decryption → merge.

## Workflow Overview

```
User provides course URL → Login (WeChat QR) → Get course list → 
Extract m3u8 per video → Download & decrypt → MP4 files
```

---

## Step 1: Gather Course Information

Ask the user for their course column URL. It typically looks like:
```
https://appvvutermf4498.pc.xiaoe-tech.com/p/t_pc/course_pc_detail/column/p_5ef1f421a523f_xHcyCVLp
```

Extract two identifiers:
- **APP_ID**: The subdomain before `.pc.xiaoe-tech.com` (e.g., `appvvUtErmF4498`)
- **COLUMN_ID**: The last path segment starting with `p_` (e.g., `p_5ef1f421a523f_xHcyCVLp`)

Also note the **base URL**: `https://{APP_ID_LOWERCASE}.pc.xiaoe-tech.com`

---

## Step 2: Login via WeChat QR Code

Use the browser tool to navigate to the course page and trigger login:

1. Navigate to the base URL
2. Click the "登录" (Login) button
3. Wait for the login dialog to appear
4. Use `evaluate` to get the QR code from canvas:
   ```javascript
   var canvas = document.querySelector('.qrcode-content canvas');
   if (canvas) { canvas.toDataURL('image/png'); }
   ```
5. Save QR as PNG file and display to user
6. User scans with WeChat
7. Verify login by checking "登录" button disappears

**Important**: Keep browser session alive. Timeout requires re-login.

---

## Step 3: Get Course List

Call the course column API from browser evaluate:

```javascript
const courses = [];
for (let page = 1; page <= 20; page++) {
  const resp = await fetch("/xe.course.business.sale.before.column.items.get/1.0.0", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({column_id: COLUMN_ID, page_index: page, size: 10})
  });
  const data = await resp.json();
  if (data.code !== 0 || !data.data?.list?.length) break;
  courses.push(...data.data.list);
  if (courses.length >= data.data.total) break;
}
```

Save to `courses_list.json`. Each entry has `resource_id`, `resource_title`.

---

## Step 4: Check Existing Files

Check user's target directory and temp directory. Use fuzzy matching 
(first 20 characters of normalized names) to determine which courses 
need downloading. Normalize names by:
- Removing leading "视频" prefix
- Collapsing multiple spaces
- Stripping trailing spaces

---

## Step 5: Extract M3U8 URLs

For each missing video, navigate browser to:
```
https://{APP_ID_LOWERCASE}.pc.xiaoe-tech.com/p/t_pc/course_pc_detail/video/{resource_id}
```

Wait 3-5 seconds, then extract:

```javascript
var h = document.documentElement.innerHTML;
var i = h.indexOf('m3u8');
if (i > -1) {
  return h.substring(Math.max(0, i-300), i+200)
          .match(/https?:\/\/[^"'\s<>]*\.m3u8[^"'\s<>]*/)[0]
          .replace(/&amp;/g, '&');
}
```

Prefer `hd-encrypt-stream.m3u8` over `sd-encrypt-stream.m3u8`.

Possible CDN domains:
- `vta.vod.xiaoe-materials.com`
- `material-ali.vod.xiaoe-materials.com`
- `c-vod-hw-k.xiaoeknow.com`
- `v-vod-k.xiaoeknow.com`
- `v-tos-k.xiaoeknow.com`

---

## Step 6: Extract Key URL from M3U8

Use the bundled `scripts/gk.py` on each m3u8 URL:

```bash
python <skill-dir>/scripts/gk.py "<m3u8_url>"
```

It outputs `KEY=<url>` and `SEGS=<count>`. The key URL formats vary:
- Ali: `material-api.xiaoeknow.com/.../keys?edk=...&app_id=...`
- HW: `app.xiaoe-tech.com/.../hw.vod.get/1.0.0?asset_id=...`
- TOS: `app.xiaoe-tech.com/.../zj.vod.get/.../keys?ak=...&source=jarvis`

---

## Step 7: Download, Decrypt, Merge

Use the bundled `scripts/dl_fast.py` for each video:

```bash
python <skill-dir>/scripts/dl_fast.py "<course_name>" "<m3u8_url>" "<key_url>"
```

This script:
1. Downloads the 16-byte AES-128 key (needs cookies from browser session)
2. Downloads TS segments in parallel (8 threads)
3. Decrypts with AES-128-CBC (IV = 16 bytes of 0x00, NO PKCS7 unpadding)
4. Merges segments into MP4

**Cookies**: Extract from browser's `document.cookie` after login. Essential: 
`pc_user_key`, `logintime`, `xenbyfpfUnhLsdkZbX`, `show_user_icon`.

**Output**: `%TEMP%\xiaoe_videos\<course_name>.mp4`. Guide user to copy to 
target directory after all downloads complete.

---

## Step 8: Verify and Handle Failures

After all downloads:
1. Count files in output directory
2. Run coverage check against course list
3. For any missing, re-extract fresh m3u8 URLs (tokens expire)
4. `exitCode 1` means likely token expiry — redo extraction
5. Report remaining gaps and retry

---

## Technical Reference

### AES Decryption Details
- Algorithm: AES-128-CBC
- IV: 16 bytes of `0x00`
- Key: Raw 16 bytes from key API (already server-decrypted, no XOR needed)
- No PKCS7 unpadding (TS packet format)

### M3U8 Token Format
URLs contain time-limited query params: `?sign=<md5>&t=<hex_ts>&us=<base64>`. 
Extract fresh URLs just before downloading.

### Cookie Lifecycle
Session-based cookies. Browser close = invalidated. Timeout ~1-2 hours. 
Download in small batches for long-running sessions.
