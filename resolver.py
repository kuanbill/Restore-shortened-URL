import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re


def resolve_url(short_url: str) -> str:
    try:
        resp = requests.get(
            short_url,
            allow_redirects=True,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Request failed: {e}")

    final_url = resp.url
    original_domain = urlparse(short_url).netloc
    final_domain = urlparse(final_url).netloc

    if original_domain != final_domain:
        return final_url

    soup = BeautifulSoup(resp.text, "html.parser")

    hidden = soup.find("input", {"id": "target"})
    if hidden and hidden.get("value"):
        return hidden["value"]

    meta = soup.find("meta", attrs={"http-equiv": re.compile(r"refresh", re.I)})
    if meta and meta.get("content"):
        m = re.search(r"url\s*=\s*(.+)", meta["content"], re.I)
        if m:
            return m.group(1).strip()

    for script in soup.find_all("script"):
        if script.string:
            m = re.search(
                r"(?:window\.)?location(?:\.href)?\s*=\s*['\"]([^'\"]+)['\"]",
                script.string,
            )
            if m:
                return m.group(1)

    return final_url
