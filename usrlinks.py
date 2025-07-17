import os
import sys
import time
import requests
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor

# Import styling libraries
try:
    from colorama import init, Fore, Back, Style
    from pyfiglet import Figlet
    from tqdm import tqdm
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    import rich.box as box
except ImportError:
    print("Required libraries not found. Installing now...")
    os.system("pip install colorama pyfiglet tqdm rich requests")
    from colorama import init, Fore, Back, Style
    from pyfiglet import Figlet
    from tqdm import tqdm
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    import rich.box as box

# Initialize colorama
init(autoreset=True)

# Constants
PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://instagram.com/{}",
    "Reddit": "https://reddit.com/user/{}",
    "TikTok": "https://tiktok.com/@{}",
    "Pinterest": "https://pinterest.com/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "YouTube": "https://youtube.com/{}",
    "Twitch": "https://twitch.tv/{}",
    "Vimeo": "https://vimeo.com/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "DeviantArt": "https://{}.deviantart.com",
    "Flickr": "https://flickr.com/people/{}",
    "Medium": "https://medium.com/@{}",
    "Quora": "https://quora.com/profile/{}",
    "Tumblr": "https://{}.tumblr.com",
    "WordPress": "https://{}.wordpress.com",
    "Spotify": "https://open.spotify.com/user/{}",
    "Patreon": "https://patreon.com/{}",
    "Wikipedia": "https://en.wikipedia.org/wiki/User:{}",
    "Slack": "https://{}.slack.com",
    "Discord": "https://discordapp.com/users/{}",  # Note: Discord usernames have #discriminator
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Initialize console
console = Console()

class UsernameChecker:
    def __init__(self, verbose: bool = False, use_tor: bool = False):
        self.verbose = verbose
        self.use_tor = use_tor
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        
        if use_tor:
            self._configure_tor()

    def _configure_tor(self):
        """Configure session to use Tor proxy"""
        try:
            self.session.proxies = {
                'http': 'socks5h://127.0.0.1:9050',
                'https': 'socks5h://127.0.0.1:9050'
            }
            # Test Tor connection
            test_url = "https://check.torproject.org/api/ip"
            response = self.session.get(test_url)
            if "Congratulations" not in response.text:
                console.print("[red]Tor is not working properly. Falling back to direct connection.[/red]")
                self.use_tor = False
                self.session.proxies = {}
            else:
                console.print("[green]✓ Tor connection established[/green]")
        except Exception as e:
            console.print(f"[red]Tor configuration failed: {e}[/red]")
            self.use_tor = False
            self.session.proxies = {}

    def check_username(self, username: str, platform: str) -> Dict[str, str]:
        """Check username availability on a specific platform"""
        url = PLATFORMS[platform].format(username)
        result = {
            "platform": platform,
            "username": username,
            "url": url,
            "status": "Unknown",
            "available": None
        }

        try:
            if platform == "GitHub":
                response = self.session.get(f"https://api.github.com/users/{username}", timeout=10)
                result["available"] = response.status_code == 404
            elif platform == "Twitter":
                response = self.session.get(f"https://twitter.com/{username}", timeout=10)
                result["available"] = response.status_code == 404 or "This account doesn't exist" in response.text
            elif platform == "Instagram":
                response = self.session.get(f"https://www.instagram.com/{username}/?__a=1", timeout=10)
                result["available"] = response.status_code == 404
            elif platform == "Reddit":
                response = self.session.get(f"https://www.reddit.com/user/{username}/about.json", timeout=10)
                result["available"] = response.status_code == 404
            elif platform == "TikTok":
                response = self.session.get(f"https://www.tiktok.com/@{username}", timeout=10)
                result["available"] = response.status_code == 404 or "Couldn't find this account" in response.text
            else:
                # Generic check for other platforms
                response = self.session.get(url, timeout=10)
                result["available"] = response.status_code == 404

            if result["available"] is not None:
                result["status"] = "✅ Available" if result["available"] else "❌ Taken"
            
            if self.verbose:
                console.print(f"[yellow][VERBOSE] {platform}: Status {response.status_code}[/yellow]")

        except requests.exceptions.RequestException as e:
            if self.verbose:
                console.print(f"[red][VERBOSE] {platform}: Error - {str(e)}[/red]")
            result["status"] = f"⚠️ Error ({str(e)})"
            result["available"] = None

        return result

    def check_all_platforms(self, username: str) -> List[Dict[str, str]]:
        """Check username across all platforms using threading"""
        results = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for platform in PLATFORMS:
                futures.append(executor.submit(self.check_username, username, platform))
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task(f"[cyan]Checking {username}...", total=len(futures))
                for future in futures:
                    results.append(future.result())
                    progress.update(task, advance=1)
        
        return results

def display_banner():
    """Display the USRLINKS banner"""
    console.print("\n")
    f = Figlet(font='slant')
    banner = f.renderText('USRLINKS')
    console.print(f"[bright_green]{banner}[/bright_green]")
    console.print("[bright_cyan]Social Media Username Availability Checker[/bright_cyan]")
    console.print("[bright_white]https://github.com/yourusername/usrlinks[/bright_white]\n")

def validate_username(username: str) -> bool:
    """Validate the username format"""
    if not username:
        return False
    if len(username) < 3 or len(username) > 30:
        return False
    if ' ' in username:
        return False
    # Add more validation rules as needed
    return True

def display_results(results: List[Dict[str, str]], username: str):
    """Display results in a formatted table"""
    table = Table(title=f"Results for [bold magenta]{username}[/bold magenta]", box=box.ROUNDED)
    
    table.add_column("Platform", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("URL", style="blue")

    for result in sorted(results, key=lambda x: x['platform']):
        status_style = "green" if result['available'] else "red" if result['available'] is False else "yellow"
        table.add_row(
            result['platform'],
            f"[{status_style}]{result['status']}[/{status_style}]",
            result['url']
        )

    console.print(table)

def save_results(results: List[Dict[str, str]], username: str):
    """Save results to a CSV file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"usrlinks_results_{username}_{timestamp}.csv"
    
    try:
        with open(filename, 'w') as f:
            f.write("Platform,Status,URL\n")
            for result in results:
                f.write(f"{result['platform']},{result['status']},{result['url']}\n")
        console.print(f"[green]✓ Results saved to {filename}[/green]")
    except Exception as e:
        console.print(f"[red]Error saving results: {e}[/red]")

def read_usernames_from_file(filename: str) -> List[str]:
    """Read usernames from a text file"""
    try:
        with open(filename, 'r') as f:
            usernames = [line.strip() for line in f.readlines() if line.strip()]
        return usernames
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        return []

def main():
    parser = argparse.ArgumentParser(description='USRLINKS - Social Media Username Availability Checker')
    parser.add_argument('-u', '--username', help='Username to check')
    parser.add_argument('-f', '--file', help='Text file containing usernames to check (one per line)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
    parser.add_argument('-t', '--tor', action='store_true', help='Use Tor for anonymity')
    args = parser.parse_args()

    display_banner()

    checker = UsernameChecker(verbose=args.verbose, use_tor=args.tor)

    if args.file:
        usernames = read_usernames_from_file(args.file)
        if not usernames:
            console.print("[red]No valid usernames found in the file.[/red]")
            return
    elif args.username:
        usernames = [args.username]
    else:
        usernames = [console.input("[bold cyan]Enter a username to check: [/bold cyan]").strip()]

    for username in usernames:
        if not validate_username(username):
            console.print(f"[red]Invalid username: {username}[/red]")
            continue

        results = checker.check_all_platforms(username)
        display_results(results, username)

        if len(usernames) == 1:  # Only ask to save if checking a single username
            save_option = console.input("[bold cyan]Save results to file? (Y/N): [/bold cyan]").strip().lower()
            if save_option == 'y':
                save_results(results, username)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Operation cancelled by user.[/red]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]An error occurred: {e}[/red]")
        sys.exit(1)