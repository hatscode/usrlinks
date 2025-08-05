#!/bin/bash

# USRLINKS Simple Launcher
# Usage: ./usrlinks.sh -u username [options]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if username is provided
if [[ "$*" != *"-u"* ]] && [[ "$*" != *"--username"* ]]; then
    echo -e "${RED}Error: Username required${NC}"
    echo "Usage: $0 -u username [options]"
    echo ""
    echo "Options:"
    echo "  -u, --username    Username to scan"
    echo "  --deep-scan       Perform deep reconnaissance"
    echo "  --list-platforms  List supported platforms"
    echo "  --generate-dorks  Generate Google dorks"
    echo ""
    echo "Example: $0 -u john_doe --deep-scan"
    exit 1
fi

# Extract username from arguments
USERNAME=""
for i in "$@"; do
    if [[ $prev == "-u" ]] || [[ $prev == "--username" ]]; then
        USERNAME="$i"
        break
    fi
    prev="$i"
done

echo -e "${BLUE}🚀 Starting USRLINKS Scanner...${NC}"
echo ""

# Create results directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/results"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Run the Python script and capture output
echo -e "${YELLOW}[*] Scanning username: $USERNAME${NC}"
cd "$SCRIPT_DIR"

# Run usrlinks.py with both JSON output and display results
echo -e "${YELLOW}[*] Running USRLINKS scan...${NC}"
python3 usrlinks.py "$@" --output json

# Find the generated JSON file
JSON_FILE=$(ls USRLINKS_${USERNAME}_*.json 2>/dev/null | head -1)

if [ -z "$JSON_FILE" ]; then
    echo -e "${RED}[!] No JSON results file found. Scan may have failed.${NC}"
    exit 1
fi

echo -e "${GREEN}[+] Scan completed successfully${NC}"
echo -e "${YELLOW}[*] Generating HTML report...${NC}"

# Create HTML report
HTML_FILE="results/USRLINKS_Report_${USERNAME}_${TIMESTAMP}.html"

# Read JSON data and escape it properly for JavaScript
JSON_DATA=$(cat "$JSON_FILE" | python3 -c "
import sys
import json
try:
    data = json.load(sys.stdin)
    print(json.dumps(data))
except:
    print('[]')
")

cat > "$HTML_FILE" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>USRLINKS Report - $USERNAME</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            padding: 30px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border-radius: 10px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #667eea;
        }
        .summary-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .results-table th,
        .results-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .results-table th {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }
        .results-table tr:hover {
            background-color: #f5f5f5;
        }
        .status-available {
            color: #28a745;
            font-weight: bold;
        }
        .status-taken {
            color: #dc3545;
            font-weight: bold;
        }
        .status-error {
            color: #ffc107;
            font-weight: bold;
        }
        .recon-section {
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            color: #666;
        }
        .url-link {
            color: #667eea;
            text-decoration: none;
        }
        .url-link:hover {
            text-decoration: underline;
        }
        .recon-item {
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #17a2b8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 USRLINKS Report</h1>
            <h2>Username: $USERNAME</h2>
            <p>Generated on $(date)</p>
        </div>

        <div id="summary" class="summary">
            <!-- Summary will be populated by JavaScript -->
        </div>

        <table class="results-table">
            <thead>
                <tr>
                    <th>Platform</th>
                    <th>Status</th>
                    <th>URL</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody id="results-body">
                <!-- Results will be populated by JavaScript -->
            </tbody>
        </table>

        <div id="recon-data" class="recon-section" style="display: none;">
            <h3>🕵️ Reconnaissance Data</h3>
            <div id="recon-content"></div>
        </div>

        <div class="footer">
            <p><strong>USRLINKS</strong> - OSINT Username Hunter</p>
            <p>Scan completed at $(date)</p>
        </div>
    </div>

    <script>
        // Load JSON data
        const results = $JSON_DATA;
        
        // Calculate summary statistics
        let available = 0, taken = 0, errors = 0;
        results.forEach(result => {
            if (result.available === true) available++;
            else if (result.available === false) taken++;
            else errors++;
        });

        // Populate summary
        document.getElementById('summary').innerHTML = \`
            <div class="summary-card">
                <div class="summary-number">\${available}</div>
                <div>Available</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">\${taken}</div>
                <div>Taken</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">\${errors}</div>
                <div>Errors</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">\${results.length}</div>
                <div>Total Platforms</div>
            </div>
        \`;

        // Populate results table
        const tbody = document.getElementById('results-body');
        results.sort((a, b) => a.platform.localeCompare(b.platform)).forEach(result => {
            const row = document.createElement('tr');
            
            let statusClass = 'status-error';
            let statusText = 'ERROR';
            let actionButton = '';
            
            if (result.available === true) {
                statusClass = 'status-available';
                statusText = '✅ AVAILABLE';
                actionButton = \`<a href="\${result.url}" target="_blank" class="url-link">Visit</a>\`;
            } else if (result.available === false) {
                statusClass = 'status-taken';
                statusText = '❌ TAKEN';
                actionButton = \`<a href="\${result.url}" target="_blank" class="url-link">View Profile</a>\`;
            }
            
            row.innerHTML = \`
                <td><strong>\${result.platform}</strong></td>
                <td class="\${statusClass}">\${statusText}</td>
                <td><a href="\${result.url}" target="_blank" class="url-link">\${result.url}</a></td>
                <td>\${actionButton}</td>
            \`;
            tbody.appendChild(row);
        });

        // Check for reconnaissance data
        const hasReconData = results.some(r => r.recon_data && Object.keys(r.recon_data).length > 0);
        if (hasReconData) {
            document.getElementById('recon-data').style.display = 'block';
            let reconHtml = '<h4>🔍 Deep Scan Results</h4>';
            
            results.forEach(result => {
                if (result.recon_data && Object.keys(result.recon_data).length > 0) {
                    reconHtml += \`<div class="recon-item">
                        <h5>\${result.platform}</h5>
                        <pre style="background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto;">\${JSON.stringify(result.recon_data, null, 2)}</pre>
                    </div>\`;
                }
            });
            
            document.getElementById('recon-content').innerHTML = reconHtml;
        }
    </script>
</body>
</html>
EOF

echo -e "${GREEN}[+] HTML report generated: $HTML_FILE${NC}"

# Open the HTML file in default browser
if command -v xdg-open > /dev/null; then
    echo -e "${BLUE}[*] Opening report in browser...${NC}"
    xdg-open "$HTML_FILE"
elif command -v open > /dev/null; then
    open "$HTML_FILE"
else
    echo -e "${YELLOW}[*] Please open the following file in your browser:${NC}"
    echo -e "${GREEN}file://$(realpath "$HTML_FILE")${NC}"
fi

# Clean up JSON file optionally
read -p "Delete temporary JSON file? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm "$JSON_FILE"
    echo -e "${GREEN}[+] Temporary files cleaned up${NC}"
fi

echo -e "${GREEN}[+] Scan complete! Report saved to: $HTML_FILE${NC}"
