<img width="1013" height="396" alt="image" src="https://github.com/user-attachments/assets/1eef4979-5b1d-43cf-8d23-5e7329296408" />


# USRLINKS - The Ultimate Username OSINT tool

USRLINKS is a Python reconnaissance tool that checks username availability across multiple social media platforms. Designed for security professionals and penetration testers, it features a hacker-themed interface with bold blue styling. The tool supports single username checks or bulk scanning from files, with optional Tor anonymity and CSV report generation.

Simply install with `pip install -r requirements.txt` and run `python usrlinks.py -u username` to scan platforms like GitHub, Twitter, Instagram, Reddit and more. USRLINKS provides clear visual feedback with colored status indicators (✓ Available/✗ Taken) and preserves results for further analysis. The lightweight tool requires only Python 3.5+ and common libraries like requests and colorama.


Here's how to clone and use USRLINKS, formatted for your GitHub repository:

## 📥 Installation & Usage Guide

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/USRLINKS.git
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

### 🚀 Basic Usage
```bash
python usrlinks.py -u username
```

### 🔍 Advanced Options
```bash
# Scan multiple usernames from file
python usrlinks.py -f usernames.txt

# Use Tor for anonymity
python usrlinks.py -u username --tor

# Save results to CSV
python usrlinks.py -u username -o csv

# Increase threads for faster scanning
python usrlinks.py -u username --threads 20
```

### 📋 Full Command Options
```bash
python usrlinks.py --help
```
```
USRLINKS - The Ultimate Username OSINT Tool

Options:
  -u, --username TEXT    Username to scan
  -f, --file PATH        File containing usernames (one per line)
  -t, --tor              Use Tor for anonymity
  -o, --output [csv|json]  Save results to file
  --threads INTEGER      Number of threads (default: 10)
  --help                 Show this message and exit
```

### 🖼️ Example Output
```
Scanning username: alex
+------------+-----------+-----------------------------+
| Platform   | Status    | URL                         |
+------------+-----------+-----------------------------+
| GitHub     | ✓ Available | https://github.com/alex    |
| Twitter    | ✗ Taken     | https://twitter.com/alex   |
| Instagram  | ✗ Taken     | https://instagram.com/alex |
+------------+-----------+-----------------------------+
```

### 📦 Dependencies
- Python 3.5+
- requests
- beautifulsoup4
- fake-useragent
- tqdm
- dnspython
- pysocks (for Tor support)

### 🔧 Troubleshooting
If you encounter SSL errors:
```bash
pip install --upgrade certifi
```

For Tor connectivity issues:
```bash
sudo service tor start  # Linux
brew services start tor # Mac
```
