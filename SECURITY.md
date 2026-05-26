# Security

Do not commit:

- secrets, access tokens, refresh tokens, connection strings, private keys, or tenant credentials;
- private environment URLs, tenant IDs, client names, exported run payloads, screenshots, logs, or production data;
- solution ZIPs, unpacked solution exports, temporary debug folders, or flow run artifacts.

Use placeholders such as `<environment-url>`, `<solution-name>`, `<flow-name>`, `<connection-reference>`, and `<sharepoint-site-url>`.

Before publishing, run:

```bash
bash scripts/validate-skill.sh
git diff --check
```
