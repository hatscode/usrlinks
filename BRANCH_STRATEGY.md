# USRLINKS Branch Strategy

## Repository Structure

This repository maintains a clear separation between different implementation approaches:

### Main Branch (`main`)
- **Purpose**: Terminal-based OSINT tool
- **Target Users**: Security professionals, penetration testers, CLI enthusiasts
- **Key Features**:
  - Command-line interface
  - Static HTML report generation
  - CSV/JSON export capabilities
  - Lightweight and portable
  - No web server dependencies

### Web UI Branch (`web-ui`) - Community Maintained
- **Purpose**: Web-based interface for USRLINKS
- **Target Users**: Users preferring graphical interfaces
- **Key Features**:
  - Web dashboard
  - Real-time scanning
  - Browser-based reports
  - May include Flask/Django/FastAPI

## Why This Separation?

### Terminal Version Benefits:
1. **Security**: No web server attack surface
2. **Portability**: Runs anywhere Python runs
3. **Integration**: Easy to integrate with other CLI tools
4. **Performance**: Lower resource overhead
5. **Scripting**: Perfect for automation and batch processing

### Web Version Benefits:
1. **Accessibility**: Easier for non-technical users
2. **Visualization**: Rich graphical interfaces
3. **Collaboration**: Easy to share with teams
4. **Real-time**: Live updates and progress tracking

## Contributing Guidelines

### To Main Branch (Terminal)
```bash
# Clone and work on terminal features
git clone https://github.com/stilla1ex/usrlinks.git
cd usrlinks
git checkout main
# Make your terminal-focused changes
git checkout -b feature/your-terminal-enhancement
```

### To Web UI Branch
```bash
# Clone and work on web features
git clone https://github.com/stilla1ex/usrlinks.git
cd usrlinks
git checkout -b web-ui origin/web-ui  # If exists, or create new
# Make your web-focused changes
git checkout -b feature/your-web-enhancement
```

## Pull Request Guidelines

### For Main Branch (Terminal)
- ✅ New platform integrations
- ✅ Performance improvements
- ✅ Enhanced reconnaissance features
- ✅ Better terminal output formatting
- ✅ Export format improvements
- ❌ Web servers or frameworks
- ❌ Browser-based interfaces

### For Web UI Branch
- ✅ Web frameworks (Flask, Django, etc.)
- ✅ Frontend interfaces
- ✅ Web dashboards
- ✅ Real-time features
- ❌ Changes to core terminal functionality

## Maintainer Notes

As the project maintainer, you can:

1. **Reject web-based PRs to main**: Politely redirect to web-ui branch
2. **Set branch protection**: Require reviews for main branch
3. **Use PR templates**: Guide contributors to the right branch
4. **Community governance**: Let community maintain web branch if desired

## Example Response to Web-Based PR

```
Thank you for your contribution! However, this repository maintains a terminal-first 
approach on the main branch. 

Your web-based enhancements would be perfect for the `web-ui` branch. Please:

1. Rebase your changes onto the `web-ui` branch
2. Update your PR target to `web-ui` instead of `main`
3. Ensure your changes don't modify core terminal functionality

This helps us maintain both approaches for different user needs.
```
