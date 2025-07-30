<img width="1013" height="396" alt="image" src="https://github.com/user-attachments/assets/1eef4979-5b1d-43cf-8d23-5e7329296408" />

# USRLINKS - The Ultimate OSINT Username Hunter

USRLINKS is an advanced Python reconnaissance tool that checks username availability across 100+ social media platforms and performs deep OSINT intelligence gathering. Designed for security professionals, penetration testers, and OSINT investigators, this tool goes beyond simple username checking to extract valuable profile information, contact details, and generate comprehensive investigation reports.

## ✨ Key Features

- 🔍 **Username Scanning**: Check availability across 100+ platforms
- 🕵️ **Deep Reconnaissance**: Extract emails, phone numbers, location data, and bio information
- 🖼️ **Profile Image Analysis**: Download and hash profile images for comparison
- 🔗 **Google Dorks Generation**: Auto-generate search queries for additional investigation
- 🌐 **Tor & Proxy Support**: Anonymous scanning with Tor or custom proxies
- 📊 **Professional Reports**: Export results to CSV/JSON with detailed intelligence data
- 🎨 **Beautiful UI**: Unicode table borders with color-coded status indicators
- ⚡ **Multi-threaded**: Fast concurrent scanning with progress tracking

## 📥 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/stilla1ex/USRLINKS.git
cd USRLINKS
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate   # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 📦 Dependencies
- Python 3.7+
- requests
- beautifulsoup4
- fake-useragent
- tqdm
- dnspython
- pysocks (for Tor support)

## 🚀 Usage Guide

### Basic Username Scan
```bash
python3 usrlinks.py -u john_doe
```

### Deep OSINT Reconnaissance
```bash
python3 usrlinks.py -u john_doe --deep-scan
```

### Generate Google Dorks
```bash
python3 usrlinks.py -u john_doe --generate-dorks
```

### Anonymous Scanning with Tor
```bash
python3 usrlinks.py -u john_doe --tor --deep-scan
```

### Export Results
```bash
python3 usrlinks.py -u john_doe --deep-scan -o csv
python3 usrlinks.py -u john_doe --deep-scan -o json
```

### Custom Proxy Usage
```bash
python3 usrlinks.py -u john_doe -p http://127.0.0.1:8080
```

### High-Speed Scanning
```bash
python3 usrlinks.py -u john_doe --threads 20
```

## 📋 Complete Command Reference

```bash
python3 usrlinks.py --help
```

```
USRLINKS - OSINT Username Hunter

Options:
  -u, --username TEXT         Username to scan
  -p, --proxy TEXT           HTTP/SOCKS proxy (e.g., http://127.0.0.1:8080)
  -t, --tor                  Use Tor for anonymity
  -th, --threads INTEGER     Number of threads (default: 10)
  -o, --output [csv|json]    Save results to file
  --platforms TEXT           Path to custom platforms JSON file
  --list-platforms           List supported platforms and exit
  --deep-scan               Perform deep reconnaissance on found profiles
  --generate-dorks          Generate Google dorks for the username
  --help                    Show this message and exit
```

## 🖼️ Example Output

### Basic Scan
```
╔══════════╦═════════════╦══════════════════════════════════╗
║ Platform ║ Status      ║ URL                              ║
╠══════════╬═════════════╬══════════════════════════════════╣
║ GitHub   ║ AVAILABLE   ║ https://github.com/john_doe      ║
║ Twitter  ║ TAKEN       ║ https://twitter.com/john_doe     ║
║ LinkedIn ║ TAKEN       ║ https://linkedin.com/in/john_doe ║
╚══════════╩═════════════╩══════════════════════════════════╝
```

### Deep Scan Results
```
=== RECONNAISSANCE SUMMARY ===
📧 Email Addresses Found:
  • john.doe@example.com
  • contact@johndoe.dev

📱 Phone Numbers Found:
  • +1-555-123-4567

🔗 Associated URLs:
  • https://johndoe.dev
  • https://blog.johndoe.com

📍 Locations Found:
  • San Francisco, CA
  • New York, NY

🖼️ Profile Images:
  • GitHub: https://avatars.githubusercontent.com/u/12345
    Hash: d41d8cd98f00b204e9800998ecf8427e
```

### Google Dorks Generation
```
=== GOOGLE DORKS FOR JOHN_DOE ===
 1. "john_doe"
 2. "john_doe" site:pastebin.com
 3. "john_doe" site:github.com
 4. "john_doe" "email" OR "contact"
 5. "john_doe" inurl:resume OR inurl:cv
```

## 🎯 Supported Platforms (100+)

### Social Media & Communication
- GitHub, Twitter/X, Instagram, LinkedIn, TikTok
- Facebook, Reddit, Telegram, Discord, WhatsApp
- Snapchat, Pinterest, Tumblr, VK

### Professional & Development
- GitLab, Bitbucket, CodePen, HackerNews
- Stack Overflow, DeviantArt, Behance
- Dribbble, 99designs, Freelancer

### Gaming & Entertainment
- Steam, Twitch, YouTube, Spotify
- Xbox Live, PlayStation, Nintendo
- Roblox, Minecraft, Epic Games

### And 70+ more platforms...

View all supported platforms:
```bash
python3 usrlinks.py --list-platforms
```

## 🔧 Advanced Configuration

### Custom Platforms File
Create a custom `platforms.json` file:
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

Use with:
```bash
python3 usrlinks.py -u username --platforms platforms.json
```

## 🛡️ Privacy & Ethics

- ✅ **Rate Limited**: Respects platform ToS and implements delays
- ✅ **No Data Storage**: Doesn't store personal information permanently
- ✅ **Ethical Use**: Designed for legitimate security research
- ✅ **Tor Support**: Anonymous scanning capabilities

**⚠️ Disclaimer**: This tool is for educational and authorized testing purposes only. Users are responsible for compliance with applicable laws and platform terms of service.

## 🔧 Troubleshooting

### SSL Certificate Errors
```bash
pip install --upgrade certifi requests
```

### Tor Connectivity Issues
```bash
# Linux
sudo service tor start
sudo systemctl enable tor

# macOS
brew services start tor

# Windows
# Download and install Tor Browser, then start it
```

### Permission Errors
```bash
chmod +x usrlinks.py
```

### Missing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📊 Output Formats

### CSV Export
Includes columns: Platform, Status, URL, Emails, Phones, URLs, Location, Bio

### JSON Export
Complete structured data including reconnaissance information and metadata

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all OSINT researchers and security professionals
- Special thanks to the Python community for excellent libraries
- Inspired by tools like Sherlock and Maigret

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/stilla1ex/USRLINKS/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/stilla1ex/USRLINKS/discussions)
- 📧 **Contact**: [Your Contact Information]

---

**Made with ❤️ for the OSINT community**