# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Kloud Kompass, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

### How to Report

Email: **contact@ttox.tech**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 1 week
- **Fix and disclosure:** Coordinated with reporter

## Scope

The following are in scope:
- Credential handling and storage
- Subprocess command injection
- Configuration file parsing vulnerabilities
- Dependency vulnerabilities

The following are out of scope:
- Issues requiring physical access to the machine
- Social engineering
- Denial of service against cloud provider APIs (those are rate-limited by the provider)

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes    |

---

*© 2026 TTox.Tech. Licensed under MIT.*
