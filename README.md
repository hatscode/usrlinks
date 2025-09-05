USRLINKS
========

USRLINKS is a command-line tool for checking username availability and gathering public profile data across multiple platforms.

**Install:**
```bash
git clone https://github.com/wh1t3h4ts/usrlinks.git
cd usrlinks
pip install -r requirements.txt
chmod +x usrlinks.sh
```

**Usage:**
```bash
./usrlinks.sh -u username [options]
```
Options include `--deep-scan`, `--list-platforms`, and `--generate-dorks`.

Results are saved in the `results/` directory.

Supported platforms are listed in `config/platforms.json`.
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
- Interactive Summary Cards: Visual statistics of available/taken/error counts
- Sortable Results Table: Click-to-visit links for all platforms
- Reconnaissance Data: Detailed intelligence from deep scans
- Professional Styling: Clean, modern interface with responsive design
- Export Ready: Print-friendly layout for reporting

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

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Add new platforms to the platform database
4. Improve reconnaissance modules for better data extraction
5. Enhance the HTML reporting with new visualizations
6. Submit a pull request

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

## Contributors

We appreciate all the contributors who have helped make USRLINKS better:

- [@stilla1ex](https://github.com/stilla1ex) - Project creator and maintainer
- [@max5010cs](https://github.com/max5010cs) - Contributor

## Disclaimer

IMPORTANT: This tool is designed for:
- Educational purposes and cybersecurity research
- Authorized penetration testing with proper permission
- OSINT investigations within legal boundaries
- Security assessments of your own accounts

Users are responsible for:
- Compliance with applicable laws and regulations
- Respecting platform terms of service
- Obtaining proper authorization before testing
- Using the tool ethically and responsibly

The developers are not responsible for any misuse of this tool.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## About OSINT

Open Source Intelligence (OSINT) is the practice of collecting information from publicly available sources. USRLINKS facilitates legitimate OSINT activities by automating username reconnaissance across multiple platforms, helping security professionals identify digital footprints and potential security exposures.

---

Star this repository if you find it useful!

Found a bug? [Open an issue](https://github.com/stilla1ex/usrlinks/issues)

Have a feature request? [Start a discussion](https://github.com/stilla1ex/usrlinks/discussions)
