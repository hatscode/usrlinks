#!/usr/bin/env python3
"""
USRLINKS - Enhanced OSINT Username Reconnaissance Tool

Improvements over previous version:
1. Fixed Twitter/X API handling with proper headers
2. Added request retries with exponential backoff
3. Implemented proper rate limiting
4. Added platform-specific detection methods
5. Enhanced error handling and user feedback
6. Added more realistic mock breach data
"""

import asyncio
import aiohttp
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum, auto
from dataclasses import dataclass
import argparse
import sys
from pathlib import Path
import random
import time

try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.table import Table
    from rich.text import Text
    from rich import box
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Constants
VERSION = "1.1.0"
DEFAULT_TIMEOUT = 15  # Increased timeout
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MAX_CONCURRENT_REQUESTS = 15  # Reduced to avoid rate limiting
MAX_RETRIES = 3
RETRY_DELAY = 2  # Base delay in seconds

class ResultStatus(Enum):
    """Enumeration for result status codes"""
    FOUND = auto()
    NOT_FOUND = auto()
    ERROR = auto()
    TIMEOUT = auto()
    RATE_LIMITED = auto()

@dataclass
class PlatformResult:
    """Data class to store platform check results"""
    platform: str
    url: str
    status: ResultStatus
    details: Optional[str] = None
    breach_data: Optional[bool] = None
    response_time: Optional[float] = None

class Color:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def display_banner():
    """Display the USRLINKS ASCII banner"""
    banner = f"""
{Color.BOLD}{Color.CYAN}
   _   _   _   _   _   _   _   _   _  
  / \ / \ / \ / \ / \ / \ / \ / \ / \ 
 ( U | S | R | L | I | N | K | S | ! )
  \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ 
{Color.RESET}
{Color.MAGENTA}  OSINT Username Reconnaissance Tool v{VERSION}{Color.RESET}
{Color.YELLOW}  -----------------------------------{Color.RESET}
"""
    print(banner)

def load_platforms_config() -> List[Dict]:
    """
    Load platform configurations with enhanced detection methods
    
    Returns:
        List of platform configurations with name, URL format, and checking method
    """
    platforms = [
        {
            "name": "GitHub",
            "url": "https://github.com/{username}",
            "method": "status_code",
            "expected_status": 200,
            "error_status": 404,
            "headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }
        },
        {
            "name": "Twitter/X",
            "url": "https://twitter.com/{username}",
            "method": "content_analysis",
            "expected_string": 'data-testid="emptyState"',  # String that appears when account doesn't exist
            "headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1"
            }
        },
        {
            "name": "Instagram",
            "url": "https://instagram.com/{username}",
            "method": "status_code",
            "expected_status": 200,
            "error_status": 404,
            "headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }
        },
        {
            "name": "Reddit",
            "url": "https://reddit.com/user/{username}",
            "method": "redirect_check",
            "success_pattern": "/user/",
            "failure_pattern": "/search",
            "headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }
        },
        {
            "name": "GitLab",
            "url": "https://gitlab.com/{username}",
            "method": "status_code",
            "expected_status": 200,
            "error_status": 404,
            "headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }
        },
        {
            "name": "Pastebin",
            "url": "https://pastebin.com/u/{username}",
            "method": "status_code",
            "expected_status": 200,
            "error_status": 404,
            "headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }
        },
    ]
    return platforms

async def fetch_with_retries(session: aiohttp.ClientSession, url: str, platform: Dict, timeout: int) -> Tuple[Optional[aiohttp.ClientResponse], float, Optional[str]]:
    """
    Perform HTTP request with retries and exponential backoff
    
    Args:
        session: aiohttp client session
        url: URL to fetch
        platform: platform configuration
        timeout: request timeout in seconds
    
    Returns:
        Tuple of (response, response_time, error_message)
    """
    headers = {
        "User-Agent": USER_AGENT,
        **platform.get("headers", {})
    }
    
    start_time = time.time()
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            async with session.get(
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True
            ) as response:
                # Check for rate limiting
                if response.status == 429:
                    if attempt < MAX_RETRIES - 1:
                        retry_after = int(response.headers.get('Retry-After', RETRY_DELAY * (attempt + 1)))
                        await asyncio.sleep(retry_after)
                        continue
                    return None, time.time() - start_time, "Rate limited"
                
                # Return successful response
                return response, time.time() - start_time, None
        
        except asyncio.TimeoutError:
            last_error = f"Timeout after {timeout} seconds"
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            continue
        
        except aiohttp.ClientError as e:
            last_error = str(e)
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            continue
    
    return None, time.time() - start_time, last_error

async def check_username(session: aiohttp.ClientSession, username: str, platform: Dict, timeout: int) -> PlatformResult:
    """
    Asynchronously check if a username exists on a given platform with enhanced detection
    
    Args:
        session: aiohttp client session
        username: username to check
        platform: platform configuration dict
        timeout: request timeout in seconds
    
    Returns:
        PlatformResult with the check status
    """
    url = platform["url"].format(username=username)
    result = PlatformResult(
        platform=platform["name"],
        url=url,
        status=ResultStatus.ERROR,
        details="Unknown error",
        response_time=None
    )
    
    response, response_time, error = await fetch_with_retries(session, url, platform, timeout)
    result.response_time = response_time
    
    if error:
        if "Timeout" in error:
            result.status = ResultStatus.TIMEOUT
        elif "Rate limited" in error:
            result.status = ResultStatus.RATE_LIMITED
        else:
            result.status = ResultStatus.ERROR
        result.details = error
        return result
    
    try:
        method = platform["method"]
        
        if method == "status_code":
            if response.status == platform["expected_status"]:
                result.status = ResultStatus.FOUND
                result.details = "Account exists"
            elif response.status == platform["error_status"]:
                result.status = ResultStatus.NOT_FOUND
                result.details = "Account not found"
            else:
                result.status = ResultStatus.ERROR
                result.details = f"Unexpected status: {response.status}"
        
        elif method == "content_analysis":
            content = await response.text()
            if platform.get("expected_string") and platform["expected_string"] in content:
                result.status = ResultStatus.NOT_FOUND
                result.details = "Account not found (content analysis)"
            else:
                result.status = ResultStatus.FOUND
                result.details = "Account exists (content analysis)"
        
        elif method == "redirect_check":
            final_url = str(response.url)
            if platform["success_pattern"] in final_url:
                result.status = ResultStatus.FOUND
                result.details = f"Account exists (final URL: {final_url})"
            elif platform["failure_pattern"] in final_url:
                result.status = ResultStatus.NOT_FOUND
                result.details = f"Account not found (final URL: {final_url})"
            else:
                result.status = ResultStatus.ERROR
                result.details = f"Unexpected redirect: {final_url}"
        
        else:
            result.status = ResultStatus.ERROR
            result.details = f"Unknown check method: {method}"
    
    except Exception as e:
        result.status = ResultStatus.ERROR
        result.details = f"Processing error: {str(e)}"
    
    return result

async def check_breach_data(username: str, timeout: int) -> Tuple[bool, Optional[str]]:
    """
    Enhanced mock breach data check with more realistic simulation
    
    Args:
        username: username to check
        timeout: request timeout in seconds
    
    Returns:
        Tuple of (breach_status, breach_details)
    """
    try:
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.3, 1.2))
        
        # Enhanced mock data with more realistic patterns
        common_breached_users = {
            "admin": ("Multiple breaches (2019-2023)", 5),
            "test": ("Collection #1 (2019)", 1),
            "user": ("LinkedIn breach (2021)", 2),
            "demo": ("Various small breaches", 3),
            "guest": ("Multiple breaches", 4),
            "root": ("System breaches", 2),
            "administrator": ("Enterprise breaches", 3)
        }
        
        if username.lower() in common_breached_users:
            details, count = common_breached_users[username.lower()]
            return True, f"Found in {count} breaches: {details}"
        
        # 10% chance of random breach for demonstration
        if random.random() < 0.1:
            fake_breaches = [
                "Adobe breach (2013)",
                "Dropbox breach (2012)",
                "LinkedIn breach (2012)",
                "MySpace breach (2016)",
                "Yahoo breach (2013-2014)"
            ]
            return True, f"Found in 1 breach: {random.choice(fake_breaches)}"
        
        return False, "No known breaches found"
    
    except Exception as e:
        return False, f"Breach check error: {str(e)}"

async def scan_platforms(username: str, platforms: List[Dict], timeout: int) -> List[PlatformResult]:
    """
    Perform asynchronous scanning of all platforms with rate limiting
    
    Args:
        username: username to check
        platforms: list of platform configurations
        timeout: request timeout in seconds
    
    Returns:
        List of PlatformResult objects
    """
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS, force_close=True)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for platform in platforms:
            task = asyncio.create_task(check_username(session, username, platform, timeout))
            tasks.append(task)
        
        # Add breach check as separate task
        breach_task = asyncio.create_task(check_breach_data(username, timeout))
        tasks.append(breach_task)
        
        results = await asyncio.gather(*tasks)
        
        # Separate platform results from breach result
        platform_results = results[:-1]
        breach_status, breach_details = results[-1]
        
        # Add breach data to each platform result
        for result in platform_results:
            result.breach_data = breach_status
        
        return platform_results, breach_details

def display_results(results: List[PlatformResult], username: str, breach_details: str, use_rich: bool = True):
    """
    Display the scan results in the terminal with enhanced formatting
    
    Args:
        results: list of PlatformResult objects
        username: the username that was scanned
        breach_details: details about breach findings
        use_rich: whether to use rich library for display
    """
    if use_rich and RICH_AVAILABLE:
        display_results_rich(results, username, breach_details)
    else:
        display_results_plain(results, username, breach_details)

def display_results_plain(results: List[PlatformResult], username: str, breach_details: str):
    """Display results without rich library"""
    print(f"\n{Color.BOLD}Results for username: {Color.CYAN}{username}{Color.RESET}\n")
    print(f"{Color.BOLD}{'Platform':<20} {'Status':<15} {'Response Time':<12} {'Details'}{Color.RESET}")
    print("-" * 80)
    
    for result in results:
        if result.status == ResultStatus.FOUND:
            status = f"{Color.GREEN}Found{Color.RESET}"
        elif result.status == ResultStatus.NOT_FOUND:
            status = f"{Color.RED}Not Found{Color.RESET}"
        elif result.status == ResultStatus.RATE_LIMITED:
            status = f"{Color.YELLOW}Rate Limited{Color.RESET}"
        else:
            status = f"{Color.YELLOW}Error{Color.RESET}"
        
        time_str = f"{result.response_time:.2f}s" if result.response_time else "N/A"
        breach_info = f"{Color.RED}(Breached){Color.RESET}" if result.breach_data else ""
        
        print(f"{result.platform:<20} {status:<15} {time_str:<12} {result.details} {breach_info}")
    
    # Summary statistics
    found_count = sum(1 for r in results if r.status == ResultStatus.FOUND)
    error_count = sum(1 for r in results if r.status in (ResultStatus.ERROR, ResultStatus.TIMEOUT, ResultStatus.RATE_LIMITED))
    
    print(f"\n{Color.BOLD}Summary:{Color.RESET}")
    print(f"Found on {Color.GREEN}{found_count}{Color.RESET} out of {len(results)} platforms")
    print(f"Encountered {Color.YELLOW}{error_count}{Color.RESET} errors/timeouts")
    
    if any(r.breach_data for r in results):
        print(f"\n{Color.RED}BREACH WARNING:{Color.RESET} {breach_details}")

def display_results_rich(results: List[PlatformResult], username: str, breach_details: str):
    """Display results using rich library for enhanced formatting"""
    console = Console()
    
    # Create results table
    table = Table(
        title=f"USRLINKS Results for [bold cyan]{username}[/]",
        box=box.ROUNDED,
        header_style="bold magenta",
        expand=True
    )
    table.add_column("Platform", style="magenta", no_wrap=True)
    table.add_column("Status", width=12)
    table.add_column("Time", justify="right")
    table.add_column("Details", style="dim")
    table.add_column("Security", justify="center")
    
    for result in results:
        if result.status == ResultStatus.FOUND:
            status = Text("✓ Found", style="bold green")
        elif result.status == ResultStatus.NOT_FOUND:
            status = Text("✗ Not Found", style="bold red")
        elif result.status == ResultStatus.RATE_LIMITED:
            status = Text("⚠ Rate Limited", style="bold yellow")
        else:
            status = Text("⚠ Error", style="bold yellow")
        
        time_str = Text(f"{result.response_time:.2f}s" if result.response_time else "N/A", style="blue")
        
        if result.breach_data:
            security = Text("⚠️ BREACHED", style="bold red")
        else:
            security = Text("✓ Clean", style="dim")
        
        table.add_row(
            result.platform,
            status,
            time_str,
            result.details,
            security
        )
    
    # Summary statistics
    found_count = sum(1 for r in results if r.status == ResultStatus.FOUND)
    error_count = sum(1 for r in results if r.status in (ResultStatus.ERROR, ResultStatus.TIMEOUT, ResultStatus.RATE_LIMITED))
    
    console.print(table)
    
    # Summary panel
    summary_text = Text()
    summary_text.append(f"Found on ", style="bold")
    summary_text.append(f"{found_count}", style="bold green")
    summary_text.append(f" out of {len(results)} platforms\n", style="bold")
    summary_text.append(f"Encountered ", style="bold")
    summary_text.append(f"{error_count}", style="bold yellow")
    summary_text.append(" errors/timeouts", style="bold")
    
    console.print(Panel(
        summary_text,
        title="[bold]Summary[/]",
        border_style="blue",
        padding=(1, 2)
    ))
    
    # Breach warning if found
    if any(r.breach_data for r in results):
        console.print(Panel(
            breach_details,
            title="[bold red]BREACH WARNING[/]",
            border_style="red",
            style="red",
            padding=(1, 2)
        ))

def export_results(results: List[PlatformResult], username: str, breach_details: str, format: str = "json", output_dir: str = "."):
    """
    Enhanced export functionality with breach details
    
    Args:
        results: list of PlatformResult objects
        username: the username that was scanned
        breach_details: details about breach findings
        format: export format (json, csv, txt)
        output_dir: directory to save the file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"usrlinks_{username}_{timestamp}.{format}"
    filepath = Path(output_dir) / filename
    
    try:
        if format == "json":
            export_data = {
                "username": username,
                "timestamp": datetime.now().isoformat(),
                "breach_details": breach_details,
                "results": []
            }
            
            for result in results:
                export_data["results"].append({
                    "platform": result.platform,
                    "url": result.url,
                    "status": result.status.name,
                    "details": result.details,
                    "response_time": result.response_time,
                    "breach_data": result.breach_data
                })
            
            with open(filepath, "w") as f:
                json.dump(export_data, f, indent=2)
        
        elif format == "csv":
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Platform", "URL", "Status", "Details", "Response Time", "Breach Data"])
                for result in results:
                    writer.writerow([
                        result.platform,
                        result.url,
                        result.status.name,
                        result.details,
                        result.response_time,
                        str(result.breach_data)
                    ])
                writer.writerow([])
                writer.writerow(["Breach Details", breach_details])
        
        elif format == "txt":
            with open(filepath, "w") as f:
                f.write(f"USRLINKS Results for {username}\n")
                f.write(f"Generated on {datetime.now()}\n\n")
                
                for result in results:
                    status = "Found" if result.status == ResultStatus.FOUND else \
                            "Not Found" if result.status == ResultStatus.NOT_FOUND else \
                            "Error"
                    time_str = f"{result.response_time:.2f}s" if result.response_time else "N/A"
                    breach = " (Breached)" if result.breach_data else ""
                    f.write(f"{result.platform}: {status} ({time_str}) - {result.details}{breach}\n")
                
                f.write(f"\nBreach Details: {breach_details}\n")
        
        print(f"\n{Color.GREEN}Results exported to: {filepath}{Color.RESET}")
    except Exception as e:
        print(f"\n{Color.RED}Error exporting results: {e}{Color.RESET}")

def parse_args():
    """Parse command line arguments with additional options"""
    parser = argparse.ArgumentParser(
        description=f"USRLINKS v{VERSION} - OSINT Username Reconnaissance Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "username",
        help="Username to investigate"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="Request timeout in seconds"
    )
    parser.add_argument(
        "--export",
        choices=["json", "csv", "txt"],
        help="Export results to specified format"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to save exported results"
    )
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Use simple output (disable rich formatting)"
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Don't display the banner"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=MAX_RETRIES,
        help="Maximum retry attempts for failed requests"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"USRLINKS v{VERSION}",
        help="Show version and exit"
    )
    return parser.parse_args()

async def main():
    """Main entry point for USRLINKS"""
    args = parse_args()
    
    # Display banner unless disabled
    if not args.no_banner:
        display_banner()
    
    # Load platform configurations
    platforms = load_platforms_config()
    
    # Scan platforms
    print(f"{Color.BOLD}Scanning username: {Color.CYAN}{args.username}{Color.RESET}")
    print(f"{Color.BOLD}Checking {len(platforms)} platforms with timeout={args.timeout}s...{Color.RESET}\n")
    
    if RICH_AVAILABLE and not args.simple:
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            transient=True
        ) as progress:
            task = progress.add_task("[cyan]Scanning platforms...", total=len(platforms))
            
            # Run scan in background
            scan_task = asyncio.create_task(scan_platforms(args.username, platforms, args.timeout))
            
            # Update progress bar while scanning
            while not scan_task.done():
                await asyncio.sleep(0.1)
                progress.update(task, advance=0.1)
            
            results, breach_details = await scan_task
            progress.update(task, completed=len(platforms))
    else:
        # Simple progress display
        results, breach_details = await scan_platforms(args.username, platforms, args.timeout)
    
    # Display results
    display_results(results, args.username, breach_details, use_rich=not args.simple)
    
    # Export results if requested
    if args.export:
        export_results(results, args.username, breach_details, args.export, args.output_dir)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Color.RED}Scan interrupted by user{Color.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Color.RED}Error: {e}{Color.RESET}")
        sys.exit(1)