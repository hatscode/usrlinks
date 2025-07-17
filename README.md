<img width="582" height="220" alt="image" src="https://github.com/user-attachments/assets/861f04d2-c249-41b5-a270-e457fee6194e" />

# 🕵️‍♂️ USRLINKS - Username Recon Tool

**USRLINKS** is a Python-based, interactive terminal tool that checks the availability of a given username across multiple social media and developer platforms.  
It features a hacker-themed interface with colorful output, animations, and a dynamic banner, built for OSINT investigators, ethical hackers, and security researchers.

---

## 🎯 Features & Requirements

### 🖥️ User-Friendly Terminal UI
- Stylized ASCII banner (e.g., `USRLINKS`) using **neon colors** (green, purple, cyan).
- Use libraries like `colorama`, `rich`, or `curses` for terminal formatting.
- Loading animation (spinner or progress bar) during scanning.

### 🔤 Username Input & Validation
- Accepts **single username input** (case-insensitive).
- Validates usernames (no spaces or invalid characters).
- Supports **bulk checks** via `.txt` file upload.

### 🌐 Multi-Platform Availability Check
- Queries popular platforms:
  - Twitter / X
  - Instagram
  - GitHub
  - Reddit
  - and more...
- Uses HTTP requests (e.g., `requests`) and parses response codes.
- Gracefully handles rate-limiting, timeouts, and connection errors.

### 📊 Real-Time Results Display
- Tabular format with:
  - ✅ Available / ❌ Taken
  - Direct profile links (hyperlinked if supported).
- Option to **save results** to `.csv` or `.txt` with timestamps.

### ⚠️ Error Handling & Extras
- Warns if VPN/proxy is inactive or offline.
- Includes **verbose mode** to show request and response logs for debugging.

---

## 🧪 Example Workflow

```bash
$ python usrlinks.py

[USRLINKS] Enter a username: john_doe
🔍 Checking...

+------------+-----------+-------------------------------+
| Platform   | Status    | Link                          |
+------------+-----------+-------------------------------+
| Instagram  | ❌ Taken  | instagram.com/john_doe        |
| GitHub     | ✅ Available | github.com/john_doe          |
+------------+-----------+-------------------------------+

Save results? (Y/N): Y
