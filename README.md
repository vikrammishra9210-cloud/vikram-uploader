# TXT Leech Bot - Render-ready

## Quick setup

1. Put your credentials in Render environment variables:
   - API_ID
   - API_HASH
   - BOT_TOKEN

2. Build & deploy on Render (connect GitHub repo or upload zip).

3. After deployment, open your bot on Telegram and send `/start`.
   Then send `/upload` and follow prompts:
   - send the .txt as a document (one link per line)
   - send starting number, batch name, quality, caption, thumbnail url

## Notes
- This project uses `yt-dlp` to download media. Ensure your platform allows it.
- Thumbnail URL is optional. If provided, the file `thumb.jpg` will be downloaded and used.
