<img width="1013" height="396" alt="image" src="https://github.com/user-attachments/assets/1eef4979-5b1d-43cf-8d23-5e7329296408" />


# USRLINKS - Advanced OSINT Username Hunter

USRLINKS is a Python reconnaissance tool that checks username availability across 100+ social media platforms and performs deep OSINT intelligence gathering. Designed for security professionals, penetration testers, and OSINT investigators.

## Features

* Username scanning across 100+ platforms
* Deep reconnaissance with contact extraction
* Profile image analysis and hashing
* Google dorks generation
* Tor and proxy support
* CSV/JSON export with intelligence data
* Multi-threaded scanning

## Installation

```bash
git clone https://github.com/stilla1ex/USRLINKS.git
cd USRLINKS
pip install -r requirements.txt
```

## Usage

### Basic scan
```bash
python3 usrlinks.py -u john_doe
```

### Deep reconnaissance
```bash
python3 usrlinks.py -u john_doe --deep-scan
```

### Generate Google dorks
```bash
python3 usrlinks.py -u john_doe --generate-dorks
```

### Export results
```bash
python3 usrlinks.py -u john_doe --deep-scan -o csv
```

### Anonymous scanning
```bash
python3 usrlinks.py -u john_doe --tor
```

## Supported Platforms

GitHub, Twitter, Instagram, LinkedIn, TikTok, Facebook, Reddit, Telegram, Steam, Twitch, YouTube, Spotify, and 80+ more platforms.

View all:
```bash
python3 usrlinks.py --list-platforms
```

## Contributing

Contributions are welcome coz the project is far from being perfet. Fork the repository, make your changes, and submit a pull request.

## Disclaimer

This tool is for educational and authorized testing purposes only. Users are responsible for compliance with applicable laws and platform terms
