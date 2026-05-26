# xiaoe-downloader

小鹅通课程视频批量下载 HanaAgent Skill

## 功能

- **微信扫码登录**：浏览器自动化登录流程
- **课程发现**：逆向API获取完整课程列表（134个视频全覆盖）
- **M3U8提取**：从视频页面捕获加密HLS流地址
- **AES-128-CBC解密**：适配阿里云、华为云、火山引擎TOS等多种CDN密钥格式
- **8线程并行下载**：TS分片下载+解密+合并为MP4

## 快速开始

1. 将本skill安装到HanaAgent的skills目录
2. 确保Python 3.8+已安装cryptography库
3. 提供你的小鹅通课程专栏链接
4. 用微信扫描二维码登录
5. skill自动处理后续一切

## Skill结构

```
xiaoe-downloader/
├── SKILL.md              # Skill工作流指令
└── scripts/
    ├── gk.py             # M3U8密钥URL提取器
    └── dl_fast.py        # 多线程视频下载+解密+合并
```

## 工作流程

1. **获取课程信息**：从URL提取APP_ID和COLUMN_ID
2. **微信扫码登录**：无头浏览器打开登录页→生成二维码→用户扫码→验证登录
3. **获取课程列表**：调用API `xe.course.business.sale.before.column.items.get/1.0.0`
4. **检查已有文件**：对比本地文件和课程列表，确定待下载
5. **提取M3U8 URL**：逐个导航视频页，从HTML中提取加密流地址
6. **提取密钥URL**：下载m3u8播放列表，解析`#EXT-X-KEY`行
7. **下载+解密+合并**：8线程并行下载TS分片，AES-128-CBC解密，合并为MP4
8. **验证与重试**：检查覆盖率，对失败的重新提取和下载

## 技术细节

- **加密方式**：AES-128-CBC，IV为全零16字节，无需PKCS7去填充
- **CDN支持**：火山引擎TOS、阿里云VOD、华为云VOD
- **Cookie管理**：基于浏览器session的认证（每次登录不同）
- **Token处理**：m3u8 URL含有时效性sign/t/us参数，需即取即用

## 依赖

- HanaAgent（含浏览器工具）
- Python 3.8+
- `cryptography` Python包
- 已购买课程的小鹅通账号（微信扫码登录）

## 免责声明

本工具仅用于下载个人已购买的课程内容以便离线观看。使用者需遵守平台服务条款和版权法规。请勿用于未经授权的版权内容分发。
