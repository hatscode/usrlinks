# Contributing to USRLINKS

## Project Vision

USRLINKS is designed as a **terminal-based OSINT tool** with the following core principles:

- **Terminal-first interface**: Primary interaction through command line
- **Static report generation**: HTML reports are generated as static files, not served by a web server
- **Lightweight and portable**: No web framework dependencies
- **Security-focused**: Suitable for penetration testing and OSINT investigations

## Branch Strategy

- **`main` branch**: Terminal-only implementation (protected)
- **`web-version` branch**: For web-based contributions (if community wants this)
- **Feature branches**: For specific enhancements

## Contributing Guidelines

### For Terminal-Based Features (main branch)
✅ **Accepted contributions:**
- New platform integrations
- Enhanced reconnaissance capabilities
- Performance improvements
- Better terminal output formatting
- CSV/JSON export enhancements
- Bug fixes and security improvements

❌ **Not accepted on main branch:**
- Web servers (Flask, Django, FastAPI, etc.)
- Live web interfaces
- Real-time web dashboards
- Browser-based scanning interfaces

### For Web-Based Features (separate branch)
If you want to contribute web-based functionality:
1. Create or use the `web-version` branch
2. Ensure it doesn't modify core terminal functionality
3. Keep it as a separate application layer

## How to Contribute

1. **Fork the repository**
2. **Choose the right branch:**
   - Use `main` for terminal enhancements
   - Use `web-version` for web features
3. **Create a feature branch** from the appropriate base
4. **Submit a pull request** to the correct target branch

## Code Standards

- Maintain Python 3.6+ compatibility
- Follow existing code style
- Include proper error handling
- Add logging for debugging
- Update documentation for new features

## Testing

Before submitting:
- Test on multiple platforms
- Verify terminal output formatting
- Ensure no web framework dependencies in main branch
- Test with various usernames and edge cases

---

**Remember**: The main branch stays terminal-focused to maintain the tool's core identity and use case.
