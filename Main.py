#!/usr/bin/env python3

import requests
import os
import hashlib
import json
import subprocess
import time

DISCORD_WEBHOOK_URL = "your_webhook_link"
URLS_FILE = "urls.txt"
HISTORY_DIR = "history"
TMP_DIR = "tmp"

def send_to_discord(message):
    """Send a message to Discord with chunking."""
    for chunk in [message[i:i+2000] for i in range(0, len(message), 2000)]:
        try:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": chunk})
        except Exception as e:
            print(f"Discord send error: {str(e)}")

def get_urls_to_monitor():
    """Read URLs from monitoring list."""
    if not os.path.exists(URLS_FILE):
        raise FileNotFoundError(f"Create {URLS_FILE} with JS URLs to monitor")
    return [url.strip() for url in open(URLS_FILE, "r") if url.strip()]

def run_xnlinkfinder(url):
    """Run xnLinkFinder directly on the target URL."""
    try:
        os.makedirs(TMP_DIR, exist_ok=True, mode=0o755)
        output_file = os.path.join(TMP_DIR, f"results_{os.getpid()}.txt")
        
        # Run xnLinkFinder with URL as input
        cmd = [
            "xnLinkFinder",
            "-i", url,
            "-sf", ".",
            "-o", output_file,
            "-op", output_file
        ]
        
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30
        )
        
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                return set(line.strip() for line in f if line.strip())
        return set()
    
    except subprocess.TimeoutExpired:
        print(f"xnLinkFinder timeout for {url}")
        return None
    except Exception as e:
        print(f"xnLinkFinder error: {str(e)}")
        return None
    finally:
        # Cleanup temporary files
        if 'output_file' in locals() and os.path.exists(output_file):
            os.remove(output_file)

def monitor_url(url):
    """Monitor a URL for changes in extracted endpoints."""
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    history_file = os.path.join(HISTORY_DIR, f"{url_hash}.json")
    
    # Get current findings
    current_results = run_xnlinkfinder(url)
    if current_results is None:
        return  # Skip failed scans
    
    # Load previous results
    previous_results = set()
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                previous_results = set(json.load(f))
        except json.JSONDecodeError:
            pass
    
    # Detect and report changes
    new_entries = current_results - previous_results
    if new_entries:
        message = f"🚨 New endpoints in {url}:\n" + "\n".join(sorted(new_entries))
        send_to_discord(message)
        
        # Update history
        with open(history_file, "w") as f:
            json.dump(list(current_results), f)

def main():
    """Main monitoring loop."""
    os.makedirs(HISTORY_DIR, exist_ok=True, mode=0o755)
    
    try:
        for url in get_urls_to_monitor():
            print(f"Scanning: {url}")
            monitor_url(url)
    except Exception as e:
        print(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main()
