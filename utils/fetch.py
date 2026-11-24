"""Link-preview helper: given a URL a user pastes into a message, fetch it
server-side and extract a title/thumbnail so we can render a rich preview card."""
import requests


def fetch_preview(url):
    resp = requests.get(url, timeout=5)
    content_type = resp.headers.get("Content-Type", "")
    return {
        "url": url,
        "status": resp.status_code,
        "content_type": content_type,
        "snippet": resp.text[:500],
    }
