# twitch-finder
using twitch I'd to check if online or not


# Twitch Stream Finder

Automatically find and monitor Twitch streams from target websites.

## Setup

1. **Fork this repository**
2. **Edit `config/twitch_ids.json`** with your target URLs and default channels
3. **Run manually** via GitHub Actions tab → "Find Twitch Streams" → "Run workflow"

## Files

- `config/twitch_ids.json` - Input configuration
- `output/streams_data.json` - Output results
- `scripts/find_streams.py` - Main script

## Manual Run

1. Go to **Actions** tab
2. Click **"Find Twitch Streams"**
3. Click **"Run workflow"**
4. Wait for completion
5. Check `output/streams_data.json` for results

## Output Format

```json
{
  "last_updated": "2024-01-15T10:30:00",
  "streams": [
    {
      "channel": "arivumani1075",
      "is_live": true,
      "viewers": "1,234",
      "game": "Just Chatting",
      "m3u8_url": "https://...",
      "profile_url": "https://twitch.tv/arivumani1075"
    }
  ]
}
