# Tamil Video Generator - Project Rules

## Build & Run

```bash
pip install -r requirements.txt
python generate_once.py --skip-upload          # test locally
python generate_once.py                        # generate + upload
```

## Required Environment Variables

| Variable | Source | Required |
|---|---|---|
| `GEMINI_API_KEY` | https://ai.google.dev | Yes |
| `PEXELS_API_KEY` | https://www.pexels.com/api/ | Recommended (images fallback to gradients without it) |
| `YOUTUBE_CLIENT_ID` | Google Cloud Console | For upload |
| `YOUTUBE_CLIENT_SECRET` | Google Cloud Console | For upload |
| `YOUTUBE_REFRESH_TOKEN` | `python auth_setup.py` | For upload |

## Pipeline Architecture

```
gemini_engine  -> topic + script + metadata
screenplay_engine -> scene breakdown
visual_engine  -> Pexels stock images per scene
tts_engine     -> edge-tts per-sentence audio
video_engine   -> moviepy composition (subtitles, music, transitions)
thumbnail_engine -> 1280x720 thumbnail
quality_control -> pre-publish checks
generate_once.py -> orchestrator
youtube_uploader.py -> YouTube Data API upload
```

## Key Files

- `config.py` — all settings, paths, env vars
- `generate_once.py` — main entry point (CI/CD)
- `gemini_engine.py` — AI content generation
- `tts_engine.py` — Tamil TTS (edge-tts)
- `video_engine.py` — video composition
- `youtube_uploader.py` — YouTube upload (kept from original)

## Testing

Run locally with `--skip-upload` to verify video generation without uploading.
Check `videos/` for output MP4 and `thumbnails/` for thumbnail JPG.

## GitHub Actions Secrets

Add these in repo Settings > Secrets > Actions:
- `GEMINI_API_KEY`
- `PEXELS_API_KEY`
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`
