# TestApp

A small internal user-management API: registration, login, profile pages,
an admin user-search tool, link previews for pasted URLs, profile import/export,
and password reset.

## Run locally

```
pip install -r requirements.txt
python app.py
```

## Known open items (backlog)

- Admin search could use better fuzzy matching
- Link preview sometimes times out on slow sites
- Would be nice to add a "resend reset link" rate limit
- Profile import could support more bundle formats
- Log export UI only exposes zip/tar/tar.gz for now, might want more formats
