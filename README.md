# xiaoe-downloader

HanaAgent skill for batch downloading purchased course videos from Xiaoe-Tech (小鹅通) platform.

## Features

- **WeChat QR Login**: Automated browser-based login flow
- **Course Discovery**: Reverse-engineered API to fetch complete course lists
- **M3U8 Extraction**: Captures encrypted HLS stream URLs from video pages
- **AES-128-CBC Decryption**: Handles multi-CDN key formats (AliCloud, Huawei Cloud, Volcano Engine TOS)
- **Multi-threaded Download**: 8-thread concurrent TS segment download with decryption
- **MP4 Merge**: Combines decrypted segments into playable MP4 files

## Quick Start

1. Install this skill in your HanaAgent skills directory
2. Ensure Python 3.8+ with `cryptography` library is available
3. Provide your Xiaoe-Tech course column URL when prompted
4. Scan the QR code with WeChat to log in
5. The skill handles everything else automatically

## Skill Structure

```
xiaoe-downloader/
├── SKILL.md              # Skill workflow instructions
└── scripts/
    ├── gk.py             # M3U8 key URL extractor
    └── dl_fast.py        # Multi-threaded video downloader & decrypter
```

## Technical Details

- **Encryption**: AES-128-CBC with zero IV, no PKCS7 unpadding
- **CDN Support**: Volcano Engine TOS, AliCloud VOD, Huawei Cloud VOD
- **Cookie Management**: Session-based authentication via browser
- **Token Handling**: Time-limited m3u8 sign/t/us parameters

## Requirements

- HanaAgent with browser tool
- Python 3.8+
- `cryptography` Python package
- WeChat account with course purchase access

## Disclaimer

This tool is intended for downloading personally purchased course content for offline viewing. Users are responsible for complying with the platform's terms of service and copyright laws. Do not use this tool to distribute copyrighted content without authorization.
