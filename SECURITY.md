# Security Policy

## Supported version
Current SIM EARTH 7.07 mainline and tagged releases are the supported surfaces.

## Report a vulnerability
Please use GitHub's private vulnerability reporting feature when enabled, or contact the repository owner privately. Do not publish credentials, private sensor recordings, or exploit details in a public issue.

## Security boundaries
- never commit Apple signing certificates, Android keystores, API keys, or personal sensor datasets;
- native wrappers should preserve `contextIsolation`/no Node integration for game content;
- browser permissions should be least-privilege and user initiated;
- external data feeds should be treated as untrusted input.
