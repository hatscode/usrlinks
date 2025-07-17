#!/usr/bin/env python3
"""
USRLINKS - Social Media Username Availability Checker
Python 3.5+ compatible version
"""

import os
import sys
import time
import requests
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Import styling libraries
try:
    from colorama import init, Fore, Style
    from pyfiglet import Figlet
    from tqdm import tqdm
except ImportError:
    print("Required libraries not found. Installing now...")
    os.system("pip3 install colorama pyfiglet tqdm requests")
    from colorama import init, Fore, Style
    from pyfiglet import Figlet
    from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Constants
PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://instagram.com/{}",
    "Reddit": "https://reddit.com/user/{}",
    "TikTok": "https://tiktok.com/@{}",
    "YouTube": "https://youtube.com/{}",
    "Twitch": "https://twitch.tv/{}"
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 10

class UsernameChecker:
    def __init__(self, verbose=False, use_tor=False):
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
            response = self.session.get(test_url, timeout=REQUEST_TIMEOUT)
            if "Congratulations" not in response.text:
                print(Fore.YELLOW + "Tor is not working properly. Falling back to direct connection.")
                self.use_tor = False
                self.session.proxies = {}
            else:
                print(Fore.GREEN + "✓ Tor connection established")
        except Exception as e:
            print(Fore.RED + f"Tor configuration failed: {e}")
            self.use_tor = False
            self.session.proxies = {}

    def check_username(self, username, platform):
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
                response = self.session.get(f"https://api.github.com/users/{username}", timeout=REQUEST_TIMEOUT)
                result["available"] = response.status_code == 404
            elif platform == "Twitter":
                response = self.session.get(f"https://twitter.com/{username}", timeout=REQUEST_TIMEOUT)
                result["available"] = response.status_code == 404 or "This account doesn't exist" in response.text
            elif platform == "Instagram":
                response = self.session.get(f"https://www.instagram.com/{username}/?__a=1", timeout=REQUEST_TIMEOUT)
                result["available"] = response.status_code == 404
            elif platform == "Reddit":
                response = self.session.get(f"https://www.reddit.com/user/{username}/about.json", timeout=REQUEST_TIMEOUT)
                result["available"] = response.status_code == 404
            elif platform == "TikTok":
                response = self.session.get(f"https://www.tiktok.com/@{username}", timeout=REQUEST_TIMEOUT)
                result["available"] = response.status_code == 404 or "Couldn't find this account" in response.text
            else:
                # Generic check for other platforms
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                result["available"] = response.status_code == 404

            if result["available"] is not None:
                result["status"] = "✓ Available" if result["available"] else "✗ Taken"
            
            if self.verbose:
                print(Fore.YELLOW + f"[VERBOSE] {platform}: Status {response.status_code}")

        except requests.exceptions.RequestException as e:
            result["status"] = f"⚠ Error ({str(e)})"
            result["available"] = None
            if self.verbose:
                print(Fore.RED + f"[VERBOSE] {platform}: Error - {str(e)}")

        return result

    def check_all_platforms(self, username):
        """Check username across all platforms using threading"""
        results = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for platform in PLATFORMS:
                futures.append(executor.submit(self.check_username, username, platform))
            
            with tqdm(total=len(futures), desc=f"Checking {username}", unit="site") as pbar:
                for future in futures:
                    results.append(future.result())
                    pbar.update(1)
        
        return results

def display_banner():
    """Display the USRLINKS banner"""
    print("\n")
    """Display the USRLINKS banner with bold blue styling"""
    print(Fore.BLUE + Style.BRIGHT + r"""
     ██╗   ██╗███████╗██████╗ ██╗     ██╗███╗   ██╗██╗  ██╗███████╗
     ██║   ██║██╔════╝██╔══██╗██║     ██║████╗  ██║██║ ██╔╝██╔════╝
     ██║   ██║███████╗██████╔╝██║     ██║██╔██╗ ██║█████╔╝ ███████╗
     ██║   ██║╚════██║██╔══██╗██║     ██║██║╚██╗██║██╔═██╗ ╚════██║
     ╚██████╔╝███████║██║  ██║███████╗██║██║ ╚████║██║  ██╗███████║
      ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
    """ + Style.RESET_ALL)
    print(Fore.BLUE + "Social Media Username Availability Checker\n")

def validate_username(username):
    """Validate the username format"""
    if not username:
        return False
    if len(username) < 3 or len(username) > 30:
        return False
    if ' ' in username:
        return False
    # Add more validation rules as needed
    return True

def display_results(results, username):
    """Display results in a formatted table"""
    print(f"\nResults for {Fore.MAGENTA}{username}{Fore.RESET}:")
    print(f"+------------+-----------+-------------------+")
    print(f"| Platform   | Status    | Link              |")
    print(f"+------------+-----------+-------------------+")
    
    for result in sorted(results, key=lambda x: x['platform']):
        status_color = Fore.GREEN if result['available'] else Fore.RED if result['available'] is False else Fore.YELLOW
        print(f"| {result['platform'].ljust(10)} | {status_color}{result['status'].center(9)}{Fore.RESET} | {result['url'].ljust(17)} |")
    
    print(f"+------------+-----------+-------------------+")

def save_results(results, username):
    """Save results to a CSV file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"usrlinks_results_{username}_{timestamp}.csv"
    
    try:
        with open(filename, 'w') as f:
            f.write("Platform,Status,URL\n")
            for result in results:
                f.write(f"{result['platform']},{result['status']},{result['url']}\n")
        print(Fore.GREEN + f"✓ Results saved to {filename}")
    except Exception as e:
        print(Fore.RED + f"Error saving results: {e}")

def read_usernames_from_file(filename):
    """Read usernames from a text file"""
    try:
        with open(filename, 'r') as f:
            usernames = [line.strip() for line in f.readlines() if line.strip()]
        return usernames
    except Exception as e:
        print(Fore.RED + f"Error reading file: {e}")
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
            print(Fore.RED + "No valid usernames found in the file.")
            return
    elif args.username:
        usernames = [args.username]
    else:
        usernames = [input(Fore.CYAN + "Enter a username to check: " + Fore.RESET).strip()]

    for username in usernames:
        if not validate_username(username):
            print(Fore.RED + f"Invalid username: {username}")
            continue

        results = checker.check_all_platforms(username)
        display_results(results, username)

        if len(usernames) == 1:  # Only ask to save if checking a single username
            save_option = input(Fore.CYAN + "Save results to file? (Y/N): " + Fore.RESET).strip().lower()
            if save_option == 'y':
                save_results(results, username)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + Fore.RED + "Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")
        sys.exit(1)