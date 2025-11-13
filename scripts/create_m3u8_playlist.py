import json
import os
from datetime import datetime

def create_m3u8_playlist():
    """Create M3U8 playlist from streams_data.json"""
    
    # Load the streams data
    try:
        with open('output/streams_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: output/streams_data.json not found. Run find_streams.py first.")
        return
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in streams_data.json")
        return
    
    streams = data.get('streams', [])
    last_updated = data.get('last_updated', 'Unknown')
    
    # Filter only live streams
    live_streams = [stream for stream in streams if stream.get('is_live', False)]
    
    print(f"📊 Found {len(live_streams)} live streams out of {len(streams)} total")
    
    # Create M3U8 playlist content
    m3u8_content = [
        "#EXTM3U",
        f"# Generated: {datetime.now().isoformat()}",
        f"# Source Last Updated: {last_updated}",
        f"# Total Live Streams: {len(live_streams)}",
        ""
    ]
    
    # Add each live stream to the playlist
    for stream in live_streams:
        channel = stream.get('channel', 'Unknown')
        viewers = stream.get('viewers', '0')
        game = stream.get('game', 'Unknown Game')
        m3u8_url = stream.get('m3u8_url', '')
        
        if m3u8_url:
            # M3U8 entry format
            m3u8_content.extend([
                f"#EXTINF:-1 tvg-id=\"{channel}\" tvg-name=\"{channel}\" tvg-logo=\"\" group-title=\"Twitch\",{channel} - {viewers} viewers - {game}",
                m3u8_url,
                ""
            ])
    
    # If no live streams, add a message
    if not live_streams:
        m3u8_content.extend([
            "# No live streams currently available",
            "# Check back later or run the workflow again"
        ])
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Save M3U8 playlist
    playlist_path = 'output/twitch_streams.m3u8'
    with open(playlist_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u8_content))
    
    print(f"✅ M3U8 playlist created: {playlist_path}")
    print(f"🎯 Live streams in playlist: {len(live_streams)}")
    
    # Print summary
    if live_streams:
        print(f"\n📺 LIVE STREAMS IN PLAYLIST:")
        for stream in live_streams:
            print(f"   🟢 {stream['channel']} - {stream['viewers']} viewers - {stream['game']}")

def create_simple_playlist():
    """Create a simpler M3U8 playlist with just channel names"""
    
    try:
        with open('output/streams_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: output/streams_data.json not found")
        return
    
    streams = data.get('streams', [])
    live_streams = [stream for stream in streams if stream.get('is_live', False)]
    
    # Simple playlist format
    m3u8_content = [
        "#EXTM3U",
        f"# Twitch Live Streams - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Live: {len(live_streams)}/{len(streams)}",
        ""
    ]
    
    for stream in live_streams:
        channel = stream.get('channel', 'Unknown')
        m3u8_url = stream.get('m3u8_url', '')
        
        if m3u8_url:
            m3u8_content.extend([
                f"#EXTINF:-1,{channel}",
                m3u8_url
            ])
    
    playlist_path = 'output/twitch_simple.m3u8'
    with open(playlist_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u8_content))
    
    print(f"✅ Simple M3U8 playlist created: {playlist_path}")

def create_all_streams_playlist():
    """Create playlist with ALL streams (live + offline)"""
    
    try:
        with open('output/streams_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: output/streams_data.json not found")
        return
    
    streams = data.get('streams', [])
    live_count = len([s for s in streams if s.get('is_live', False)])
    
    m3u8_content = [
        "#EXTM3U",
        f"# All Twitch Streams - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Live: {live_count}/{len(streams)}",
        ""
    ]
    
    for stream in streams:
        channel = stream.get('channel', 'Unknown')
        is_live = stream.get('is_live', False)
        viewers = stream.get('viewers', '0')
        game = stream.get('game', 'Unknown')
        m3u8_url = stream.get('m3u8_url', '')
        
        if m3u8_url:
            status = "LIVE" if is_live else "OFFLINE"
            m3u8_content.extend([
                f"#EXTINF:-1,{channel} [{status}] - {viewers} viewers - {game}",
                m3u8_url
            ])
    
    playlist_path = 'output/twitch_all.m3u8'
    with open(playlist_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u8_content))
    
    print(f"✅ All streams M3U8 playlist created: {playlist_path}")

if __name__ == "__main__":
    print("🎬 Creating M3U8 Playlists from streams_data.json")
    print("=" * 50)
    
    create_m3u8_playlist()
    print()
    create_simple_playlist()
    print()
    create_all_streams_playlist()
