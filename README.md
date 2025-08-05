<img width="1023" height="614" alt="image" src="https://github.com/user-attachments/assets/d7d74273-e552-426b-a15d-7241193950e2" />




# USRLINKS - Advanced OSINT Username Hunter

USRLINKS is a comprehensive Python reconnaissance tool that checks username availability across 100+ social media platforms and performs deep OSINT intelligence gathering. Designed for security professionals, penetration testers, and OSINT investigators.

## Features

### Core Functionality
* **100+ Platform Coverage**: Scan username availability across major social networks, forums, and platforms
* **Deep Reconnaissance**: Extract emails, phone numbers, locations, and bio information from profiles
* **Profile Intelligence**: Analyze profile images with hash generation for cross-platform correlation
* **Google Dorks Generator**: Automatically generate targeted search queries for enhanced OSINT
* **Advanced Reporting**: Beautiful HTML reports with interactive tables and reconnaissance data
* **Export Options**: CSV and JSON formats for data analysis and integration

### Technical Features
* **Multi-threaded Scanning**: Fast concurrent processing for efficient reconnaissance
* **Proxy & Tor Support**: Anonymous scanning with SOCKS/HTTP proxy support
* **Retry Logic**: Intelligent retry mechanisms for failed requests
* **User Agent Rotation**: Anti-detection measures with randomized headers
* **Platform-Specific Detection**: Custom logic for accurate availability detection

## Installation

```bash
git clone https://github.com/stilla1ex/usrlinks.git
cd usrlinks
pip install -r requirements.txt
chmod +x usrlinks.sh
```

## Quick Start

### Simple Launcher (Recommended)
The easiest way to use USRLINKS with automatic HTML report generation:

```bash
# Basic scan with HTML report
./usrlinks.sh -u john_doe

# Deep scan with reconnaissance data
./usrlinks.sh -u john_doe --deep-scan

# List all supported platforms
./usrlinks.sh --list-platforms
```

### Direct Python Usage
For advanced users who prefer direct Python execution:

```bash
# Basic username scan
python3 usrlinks.py -u john_doe

# Deep reconnaissance scan
python3 usrlinks.py -u john_doe --deep-scan

# Generate Google dorks
python3 usrlinks.py -u john_doe --generate-dorks

# Export to JSON/CSV
python3 usrlinks.py -u john_doe --deep-scan --output json

# Anonymous scanning via Tor
python3 usrlinks.py -u john_doe --tor

# Use custom proxy
python3 usrlinks.py -u john_doe --proxy http://127.0.0.1:8080
```

### HTML Report Features
- **Interactive Summary Cards**: Visual statistics of available/taken/error counts
- **Sortable Results Table**: Click-to-visit links for all platforms
- **Reconnaissance Data**: Detailed intelligence from deep scans
- **Professional Styling**: Clean, modern interface with responsive design
- **Export Ready**: Print-friendly layout for reporting

## Supported Platforms

**Major Social Networks**: GitHub, Twitter, Instagram, LinkedIn, TikTok, Facebook, Reddit, YouTube, Twitch
**Professional**: LinkedIn, GitHub, GitLab, Bitbucket, HackerNews, Medium
**Media & Creative**: Instagram, YouTube, TikTok, Vimeo, SoundCloud, DeviantArt, Pinterest
**Gaming**: Steam, Twitch, Roblox
**Communication**: Telegram, Discord, Skype
**Marketplaces**: Etsy, eBay
**And 80+ more platforms...

View complete list:
```bash
./usrlinks.sh --list-platforms
```

## Advanced Configuration

### Custom Platforms
Create a custom `platforms.json` file to add new platforms:
```json
{
    "CustomSite": {
        "url": "https://example.com/user/{}",
        "method": "status_code", 
        "code": [404],
        "recon_enabled": true
    }
}
```

### Threading & Performance
```bash
# Adjust thread count for faster scanning
python3 usrlinks.py -u username --threads 20

# Custom timeout for slow networks  
python3 usrlinks.py -u username --timeout 30
```

## Project Structure

```
usrlinks/
├── usrlinks.py          # Main Python scanner
├── usrlinks.sh          # Simple launcher script  
├── requirements.txt     # Python dependencies
├── results/            # HTML reports directory
├── README.md           # This file
└── usrlinks.log        # Scan logs
```

## Contributing

Contributions are welcome! The project is continuously evolving. Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Add new platforms** to the platform database
4. **Improve reconnaissance modules** for better data extraction
5. **Enhance the HTML reporting** with new visualizations
6. **Submit a pull request**

### Adding New Platforms
To add a new platform, modify the `load_platforms()` function in `usrlinks.py`:
```python
"NewPlatform": {
    "url": "https://newsite.com/{}",
    "method": "status_code",
    "code": [404],
    "recon_enabled": True  # Enable for deep scanning
}
```

## Disclaimer

**IMPORTANT**: This tool is designed for:
- **Educational purposes** and cybersecurity research
- **Authorized penetration testing** with proper permission
- **OSINT investigations** within legal boundaries
- **Security assessments** of your own accounts

**Users are responsible for**:
- Compliance with applicable laws and regulations
- Respecting platform terms of service
- Obtaining proper authorization before testing
- Using the tool ethically and responsibly

**The developers are not responsible for any misuse of this tool.**

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## About OSINT

Open Source Intelligence (OSINT) is the practice of collecting information from publicly available sources. USRLINKS facilitates legitimate OSINT activities by automating username reconnaissance across multiple platforms, helping security professionals identify digital footprints and potential security exposures.

---

**⭐ Star this repository if you find it useful!**

**🐛 Found a bug? [Open an issue](https://github.com/stilla1ex/usrlinks/issues)**

**💡 Have a feature request? [Start a discussion](https://github.com/stilla1ex/usrlinks/discussions)**
