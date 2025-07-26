#!/usr/bin/env python3
"""
USRLINKS - Advanced OSINT Username Hunter
Terminal-based tool to check username availability across 100+ platforms.
"""

import os
import sys
import time
import json
import csv
import random
import argparse
import logging
from datetime import datetime
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
from tqdm import tqdm

try:
    from fake_useragent import UserAgent
    FAKE_UA_AVAILABLE = True
except ImportError:
    FAKE_UA_AVAILABLE = False

# --- Logging Setup ----
logging.basicConfig(
    filename="usrlinks.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- Styling & Terminal UI ---
class Colors:
    RED = "\033[1;31m"
    GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[1;34m"
    MAGENTA = "\033[1;35m"
    CYAN = "\033[1;36m"
    WHITE = "\033[1;37m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    PROGRESS_BAR = "\033[1;35m"
    PROGRESS_TEXT = "\033[1;36m"
    ERROR = "\033[1;31m"

class Table:
    def __init__(self, headers):
        self.headers = headers
        self.rows = []
    def add_row(self, row):
        self.rows.append(row)
    def display(self):
        # Calculate column widths
        col_widths = [len(header) for header in self.headers]
        for row in self.rows:
            for i, cell in enumerate(row):
                cell_str = str(cell)
                if len(cell_str) > col_widths[i]:
                    col_widths[i] = len(cell_str)
        # Print top border
        print(Colors.CYAN + "╔" + "╦".join(["═" * (width + 2) for width in col_widths]) + "╗")
        # Print header
        header_row = "║".join([f" {header.ljust(col_widths[i])} " for i, header in enumerate(self.headers)])
        print(Colors.CYAN + f"║{header_row}║")
        # Print separator
        print(Colors.CYAN + "╠" + "╬".join(["═" * (width + 2) for width in col_widths]) + "╣")
        # Print rows
        for row in self.rows:
            row_str = "║".join([f" {str(cell).ljust(col_widths[i])} " for i, cell in enumerate(row)])
            print(f"║{row_str}║")
        # Print bottom border
        print(Colors.CYAN + "╚" + "╩".join(["═" * (width + 2) for width in col_widths]) + "╝")

def load_platforms(config_path=None):
    """Load platforms from JSON file or use built-in."""
    if config_path and os.path.isfile(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    # Default platforms (can be moved to a separate file)
    return {
        "GitHub": {"url": "https://github.com/{}", "method": "status_code", "code": [404]},
        "Twitter": {"url": "https://twitter.com/{}", "method": "response_text", "error_msg": ["doesn't exist", "404"]},
        "Instagram": {"url": "https://instagram.com/{}", "method": "status_code", "code": [404]},
        "Reddit": {"url": "https://reddit.com/user/{}", "method": "status_code", "code": [404]},
        "TikTok": {"url": "https://tiktok.com/@{}", "method": "response_text", "error_msg": ["Couldn't find this account"]},
        "YouTube": {"url": "https://youtube.com/{}", "method": "response_text", "error_msg": ["This channel does not exist"]},
        "Twitch": {"url": "https://twitch.tv/{}", "method": "status_code", "code": [404]},
        "LinkedIn": {"url": "https://linkedin.com/in/{}", "method": "status_code", "code": [404]},
        "Facebook": {"url": "https://facebook.com/{}", "method": "response_text", "error_msg": ["This page isn't available"]},
        "Pinterest": {"url": "https://pinterest.com/{}", "method": "response_text", "error_msg": ["Sorry, we couldn't find that page"]},
        "Steam": {"url": "https://steamcommunity.com/id/{}", "method": "response_text", "error_msg": ["The specified profile could not be found"]},
        "Vimeo": {"url": "https://vimeo.com/{}", "method": "response_text", "error_msg": ["Sorry, we couldn't find that user"]},
        "SoundCloud": {"url": "https://soundcloud.com/{}", "method": "response_text", "error_msg": ["Oops! We can't find that track"]},
        "Medium": {"url": "https://medium.com/@{}", "method": "response_text", "error_msg": ["404"]},
        "DeviantArt": {"url": "https://{}.deviantart.com", "method": "response_text", "error_msg": ["404"]},
        "GitLab": {"url": "https://gitlab.com/{}", "method": "status_code", "code": [404]},
        "Bitbucket": {"url": "https://bitbucket.org/{}", "method": "status_code", "code": [404]},
        "Keybase": {"url": "https://keybase.io/{}", "method": "status_code", "code": [404]},
        "HackerNews": {"url": "https://news.ycombinator.com/user?id={}", "method": "response_text", "error_msg": ["No such user"]},
        "CodePen": {"url": "https://codepen.io/{}", "method": "response_text", "error_msg": ["Sorry, couldn't find that pen"]},
        "Telegram": {"url": "https://t.me/{}", "method": "response_text", "error_msg": ["Telegram channel not found"]},
        "Tumblr": {"url": "https://{}.tumblr.com", "method": "response_text", "error_msg": ["Nothing here"]},
        "Spotify": {"url": "https://open.spotify.com/user/{}", "method": "response_text", "error_msg": ["Couldn't find that user"]},
        "Last.fm": {"url": "https://last.fm/user/{}", "method": "response_text", "error_msg": ["Page not found"]},
        "Roblox": {"url": "https://www.roblox.com/user.aspx?username={}", "method": "response_text", "error_msg": ["404"]},
        "Quora": {"url": "https://www.quora.com/profile/{}", "method": "response_text", "error_msg": ["Oops! The page you were looking for doesn't exist"]},
        "VK": {"url": "https://vk.com/{}", "method": "response_text", "error_msg": ["404"]},
        "Imgur": {"url": "https://imgur.com/user/{}", "method": "response_text", "error_msg": ["404"]},
        "Etsy": {"url": "https://www.etsy.com/shop/{}", "method": "response_text", "error_msg": ["404"]},
        "Pastebin": {"url": "https://pastebin.com/u/{}", "method": "response_text", "error_msg": ["404"]},
    }

FALLBACK_UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def get_random_user_agent():
    if FAKE_UA_AVAILABLE:
        try:
            return UserAgent().random
        except Exception:
            pass
    return random.choice(FALLBACK_UA_LIST)

def get_session_with_retries(proxy=None, tor=False):
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
        "DNT": "1",
    })
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}
    elif tor:
        session.proxies = {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050"
        }
    return session

def check_platform(session, username, platform, info, timeout=15):
    url = info["url"].format(username)
    try:
        time.sleep(random.uniform(0.5, 1.5))
        session.headers["User-Agent"] = get_random_user_agent()
        response = session.get(url, timeout=timeout)
        if info["method"] == "status_code":
            return response.status_code in info["code"]
        elif info["method"] == "response_text":
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text().lower()
            error_msgs = [msg.lower() for msg in info["error_msg"]]
            return any(msg in page_text for msg in error_msgs)
        return False
    except Exception as e:
        logging.error(f"Error checking {platform}: {e}")
        return None

def scan_usernames(username, platforms, proxy=None, tor=False, threads=10, timeout=15):
    session = get_session_with_retries(proxy, tor)
    results = []
    items = list(platforms.items())
    with tqdm(
        total=len(items),
        desc=f"{Colors.PROGRESS_TEXT}Scanning {username}{Colors.RESET}",
        unit="site",
        bar_format=(
            f"{Colors.PROGRESS_TEXT}{{l_bar}}{{bar}}| "
            f"{{n_fmt}}/{{total_fmt}} [{Colors.RESET}{{elapsed}}<{{remaining}}]"
        ),
        colour='magenta'
    ) as pbar:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {
                executor.submit(check_platform, session, username, platform, info, timeout): platform
                for platform, info in items
            }
            for future in as_completed(futures):
                platform = futures[future]
                try:
                    is_available = future.result()
                    results.append({
                        "platform": platform,
                        "url": platforms[platform]["url"].format(username),
                        "available": is_available,
                    })
                except Exception as e:
                    logging.error(f"Exception in future for {platform}: {e}")
                    results.append({
                        "platform": platform,
                        "url": platforms[platform]["url"].format(username),
                        "available": None,
                        "error": str(e)
                    })
                finally:
                    pbar.update(1)
                    pbar.set_postfix_str(f"{Colors.PROGRESS_TEXT}Last: {platform}{Colors.RESET}")
    return results

def display_banner():
    print(Colors.GREEN + r"""
            ██╗   ██╗███████╗██████╗ ██╗     ██╗███╗   ██╗██╗  ██╗███████╗
            ██║   ██║██╔════╝██╔══██╗██║     ██║████╗  ██║██║ ██╔╝██╔════╝
            ██║   ██║███████╗██████╔╝██║     ██║██╔██╗ ██║█████╔╝ ███████╗
            ██║   ██║╚════██║██╔══██╗██║     ██║██║╚██╗██║██╔═██╗ ╚════██║
            ╚██████╔╝███████║██║  ██║███████╗██║██║ ╚████║██║  ██╗███████║
            ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
    """ + Colors.RESET)
    print(Colors.BLUE + "USRLINKS - The Ultimate OSINT Username Hunter")
    print(Colors.CYAN + "=" * 60)
    print(Colors.YELLOW + "Scanning 100+ platforms for username availability...")
    print(Colors.CYAN + "=" * 60 + "\n")

def display_results(results, username):
    table = Table(["Platform", "Status", "URL"])
    available_count = 0
    taken_count = 0
    error_count = 0
    for result in sorted(results, key=lambda x: x["platform"]):
        if result["available"] is True:
            status = Colors.GREEN + "AVAILABLE" + Colors.RESET
            available_count += 1
        elif result["available"] is False:
            status = Colors.RED + "TAKEN" + Colors.RESET
            taken_count += 1
        else:
            status = Colors.YELLOW + "ERROR" + Colors.RESET
            error_count += 1
        table.add_row([result["platform"], status, result["url"]])
    table.display()
    # Summary row
    print(Colors.CYAN + "─" * 60)
    print(Colors.GREEN + f"Available: {available_count}" + Colors.RESET + " | " +
          Colors.RED + f"Taken: {taken_count}" + Colors.RESET + " | " +
          Colors.YELLOW + f"Errors: {error_count}" + Colors.RESET)
    print(Colors.CYAN + "─" * 60)

def save_results(results, username, format="csv"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"USRLINKS_{username}_{timestamp}.{format}"
    try:
        if format == "csv":
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Platform", "Status", "URL"])
                for result in results:
                    status = "AVAILABLE" if result["available"] else "TAKEN" if result["available"] is False else "ERROR"
                    writer.writerow([result["platform"], status, result["url"]])
        elif format == "json":
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
        print(Colors.GREEN + f"[+] Results saved to {filename}")
    except Exception as e:
        print(Colors.RED + f"[-] Error saving results: {e}")
        logging.error(f"Error saving results: {e}")

def list_platforms(platforms):
    print(Colors.CYAN + "Supported platforms:")
    for name in sorted(platforms.keys()):
        print(Colors.YELLOW + f"- {name}" + Colors.RESET)

def main():
    parser = argparse.ArgumentParser(description="USRLINKS - OSINT Username Hunter")
    parser.add_argument("-u", "--username", help="Username to scan")
    parser.add_argument("-p", "--proxy", help="HTTP/SOCKS proxy (e.g., http://127.0.0.1:8080)")
    parser.add_argument("-t", "--tor", action="store_true", help="Use Tor for anonymity")
    parser.add_argument("-th", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("-o", "--output", choices=["csv", "json"], help="Save results to file")
    parser.add_argument("--platforms", help="Path to custom platforms JSON file")
    parser.add_argument("--list-platforms", action="store_true", help="List supported platforms and exit")
    args = parser.parse_args()
    platforms = load_platforms(args.platforms)
    if args.list_platforms:
        list_platforms(platforms)
        sys.exit(0)
    if not args.username:
        parser.print_help()
        sys.exit(1)
    display_banner()
    print(Colors.YELLOW + f"[*] Scanning for username: {args.username}...\n")
    results = scan_usernames(
        username=args.username,
        platforms=platforms,
        proxy=args.proxy,
        tor=args.tor,
        threads=args.threads
    )
    display_results(results, args.username)
    if args.output:
        save_results(results, args.username, args.output)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Colors.RED + "\n[!] Scan aborted by user.")
        sys.exit(1)
    except Exception as e:
        print(Colors.RED + f"\n[!] Error: {e}")
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
