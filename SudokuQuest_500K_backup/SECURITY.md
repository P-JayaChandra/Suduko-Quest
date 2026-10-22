# Security Policy

## 1. Supported Versions

| Version | Supported | Notes |
| :--- | :--- | :--- |
| 1.x (Current) | Yes | Main active branch |

---

## 2. Security Architecture

Sudoku Quest implements multiple layers of defense:

1. **Authentication & Password Storage:**
   - User passwords are never stored in plaintext. Passwords are salted and hashed using PBKDF2 with SHA-256 via Werkzeug (`generate_password_hash`).
   - Authentication tokens are cryptographically secure high-entropy tokens (`secrets.token_hex(32)`) stored with expiration timestamps.

2. **Database & SQL Injection Protection:**
   - SQLite queries utilize parameterized query substitution (`?`) exclusively to prevent SQL injection vulnerabilities.
   - Database operations enforce foreign key constraints (`PRAGMA foreign_keys=ON;`).

3. **Authoritative Game Validation:**
   - Puzzle solutions are kept hidden on the server for official game sessions.
   - Moves, hints, completion times, and XP awards are validated server-side.
   - Mistake counts and game-over states are tracked authoritatively.

4. **Web Security:**
   - CORS is configured to protect socket and REST endpoints.
   - User inputs (usernames, emails, display names) are sanitized and validated for format and length constraints.

---

## 3. Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:
- **Do not open a public issue** on GitHub.
- Submit a detailed description including steps to reproduce, impact assessment, and potential mitigations.
- Security reports will be acknowledged within 48 hours and patched promptly.
