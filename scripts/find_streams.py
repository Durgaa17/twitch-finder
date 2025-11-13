import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime

def load_config():
    """Load configuration from JSON file"""
    with open('config/twitch_ids.json', 'r') as f:
        return json.load(f)

def save_results(data):
    """Save results to output JSON file"""
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    output_data = {
        "last_updated": datetime.now().isoformat(),
        "streams": data
    }
    
    with open('output/streams_data.json', 'w') as f:
        json.dump(output_data, f, indent=2)

def scan_url_for_twitch_ids(url):
    """Scan a URL for Twitch channel IDs"""
    try:
        print(f"🔍 Scanning: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Twitch patterns to search for
        twitch_patterns = [
            r'twitch\.tv/([a-zA-Z0-9_]{4,25})',
            r'twitch\.tv/embed/([a-zA-Z0-9_]{4,25})',
            r'player\.twitch\.tv/\?channel=([a-zA-Z0-9_]{4,25})',
        ]
        
        found_streams = set()
        
        # Search in page text
        text_content = soup.get_text()
        for pattern in twitch_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            found_streams.update(matches)
        
        # Search in iframes
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            for pattern in twitch_patterns:
                matches = re.findall(pattern, src, re.IGNORECASE)
                found_streams.update(matches)
        
        # Search in scripts
        scripts = soup.find_all('script')
        for script in scripts:
            script_content = script.string or str(script)
            for pattern in twitch_patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                found_streams.update(matches)
        
        # Search in links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            for pattern in twitch_patterns:
                matches = re.findall(pattern, href, re.IGNORECASE)
                found_streams.update(matches)
        
        print(f"✅ Found {len(found_streams)} streams from {url}")
        return list(found_streams)
        
    except Exception as e:
        print(f"❌ Error scanning {url}: {e}")
        return []

def check_twitch_status(channel_name):
    """Check if a Twitch stream is live and get M3U8 URL"""
    try:
        print(f"📡 Checking: {channel_name}")
        
        # Get M3U8 URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
        }
        
        # Get stream access token
        token_url = "https://gql.twitch.tv/gql"
        query = {
            "operationName": "PlaybackAccessToken",
            "variables": {
                "isLive": True,
                "login": channel_name,
                "isVod": False,
                "vodID": "",
                "playerType": "site"
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "0828119ded1c13477966434e15800ff57ddacf13ba1911c129dc2200705b0712"
                }
            }
        }
        
        response = requests.post(token_url, headers=headers, json=query)
        data = response.json()
        
        token = data['data']['streamPlaybackAccessToken']['value']
        signature = data['data']['streamPlaybackAccessToken']['signature']
        
        # Construct m3u8 URL
        m3u8_url = f"https://usher.ttvnw.net/api/channel/hls/{channel_name}.m3u8?sig={signature}&token={token}"
        
        # Check if stream is live
        stream_url = f"https://twitch.tv/{channel_name}"
        stream_response = requests.get(stream_url, timeout=10)
        
        is_live = False
        viewers = "0"
        game = "Offline"
        
        if stream_response.status_code == 200:
            content = stream_response.text.lower()
            live_indicators = [
                '"islivebroadcast":true',
                '"isstreaming":true',
                'is_live":true',
            ]
            
            for indicator in live_indicators:
                if indicator in content:
                    is_live = True
                    # Extract viewer count
                    viewer_match = re.search(r'"viewerCount"?\s*:\s*(\d+)', content)
                    if viewer_match:
                        viewers = f"{int(viewer_match.group(1)):,}"
                    
                    # Extract game name
                    game_match = re.search(r'"game"?\s*:\s*"([^"]+)"', content)
                    if game_match:
                        game = game_match.group(1)
                    break
        
        return {
            "channel": channel_name,
            "is_live": is_live,
            "viewers": viewers,
            "game": game,
            "m3u8_url": m3u8_url,
            "profile_url": f"https://twitch.tv/{channel_name}"
        }
        
    except Exception as e:
        print(f"❌ Error checking {channel_name}: {e}")
        return {
            "channel": channel_name,
            "is_live": False,
            "viewers": "0",
            "game": "Error",
            "m3u8_url": "",
            "profile_url": f"https://twitch.tv/{channel_name}",
            "error": str(e)
        }

def main():
    """Main function to find and check streams"""
    print("🚀 Starting Twitch Stream Finder...")
    
    # Load configuration
    config = load_config()
    all_channels = set()
    
    # Scan URLs for Twitch IDs
    for url in config.get("target_urls", []):
        channels = scan_url_for_twitch_ids(url)
        all_channels.update(channels)
    
    # Add default channels
    all_channels.update(config.get("default_channels", []))
    
    print(f"📊 Total unique channels found: {len(all_channels)}")
    
    # Check status for each channel
    results = []
    for channel in sorted(all_channels):
        channel_data = check_twitch_status(channel)
        results.append(channel_data)
        
        # Add small delay to be nice to Twitch servers
        import time
        time.sleep(1)
    
    # Save results
    save_results(results)
    
    # Print summary
    live_streams = [r for r in results if r['is_live']]
    print(f"\n🎯 SUMMARY:")
    print(f"   Total channels: {len(results)}")
    print(f"   Live streams: {len(live_streams)}")
    print(f"   Results saved to: output/streams_data.json")
    
    if live_streams:
        print(f"\n🔴 LIVE NOW:")
        for stream in live_streams:
            print(f"   📺 {stream['channel']} - {stream['viewers']} viewers - {stream['game']}")

if __name__ == "__main__":
    main()
