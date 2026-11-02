# Security Policy

## Supported Versions

BlueHire is an early-stage project under active development. The following
version policy applies:

| Version | Supported          |
|---------|--------------------|
| main    | Yes (development)  |
| < main  | No                 |

Only the `main` branch on GitHub receives security patches and bug fixes.
Older releases are not maintained.

## Reporting a Vulnerability

If you discover a security vulnerability in BlueHire, please report it
responsibly. Do not create a public GitHub Issue for security matters.

### How to report

Send details of the vulnerability to the project maintainer using one of the
following routes:

1. **GitHub private vulnerability reporting**: If this feature is enabled for
   the repository, use the "Report a vulnerability" button on the Security tab
   of the GitHub repository.
2. **GitHub Issue**: Open a public Issue only if you have confirmed that the
   vulnerability does not require confidentiality, or if you have been directed
   to do so by the maintainer.

Do not post exploit code, proof-of-concept attacks, or sensitive details in
public comments or Issues.

### What to include

To help us investigate quickly, please include as much of the following as
possible:

- A clear description of the vulnerability and its impact
- Steps to reproduce the issue (including any required setup)
- The affected component(s) (e.g., authentication, API routes, database)
- The version or commit hash of BlueHire you tested against
- Any relevant logs, error messages, or screenshots
- Suggested remediation, if you have one

## Response Timeline

- **Acknowledgment**: We aim to acknowledge receipt of your report within 5
  business days.
- **Investigation**: We will investigate and provide an initial assessment
  within 10 business days.
- **Resolution**: Fixes will be developed and tested as quickly as possible,
  depending on severity and complexity.

## Disclosure

We follow coordinated disclosure practices. We ask that you do not publicly
disclose the vulnerability until we have had an opportunity to investigate and,
if needed, release a fix.

## Security Architecture Summary

BlueHire implements the following security measures:

- **Argon2 password hashing** via `pwdlib`
- **JWT authentication** with short-lived access tokens and stateful refresh
  tokens
- **Refresh token rotation** with reuse detection and forced session revocation
- **Rate limiting** on public auth endpoints (signup/login)
- **Email enumeration resistance** on login
- **Sanitized error handling** to avoid leaking implementation details

For full details, see the "Authentication Security Foundation" section of the
README.
