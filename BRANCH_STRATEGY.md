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

### Web Version Branch (`web-version`) - Community Maintained
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

## Pull Request Guidelines

### For Main Branch (Terminal)
- ✅ New platform integrations
- ✅ Performance improvements
- ✅ Enhanced reconnaissance features
- ✅ Better terminal output formatting
- ✅ Export format improvements
- ❌ Web servers or frameworks
- ❌ Browser-based interfaces

### For Web Version Branch
- ✅ Web frameworks (Flask, Django, etc.)
- ✅ Frontend interfaces
- ✅ Web dashboards
- ✅ Real-time features
- ❌ Changes to core terminal functionality
