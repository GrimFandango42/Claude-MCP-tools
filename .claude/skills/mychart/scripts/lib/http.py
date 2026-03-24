"""HTTP utilities for mychart skill (stdlib only)."""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional
from urllib.parse import urlencode

DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2.0
USER_AGENT = "mychart-skill/1.0 (Claude Code Skill)"
DEBUG = os.environ.get("MYCHART_DEBUG", "").lower() in ("1", "true", "yes")


def log(msg: str):
    """Log debug message to stderr (never stdout — stdout is for data)."""
    if DEBUG:
        sys.stderr.write(f"[mychart] {msg}\n")
        sys.stderr.flush()


class HTTPError(Exception):
    """HTTP request error with status code."""

    def __init__(self, message: str, status_code: Optional[int] = None, body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


def request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    form_data: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = MAX_RETRIES,
    raw: bool = False,
) -> Any:
    """Make an HTTP request and return parsed response.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        headers: Optional headers dict
        json_data: Optional JSON body (for POST)
        form_data: Optional form-encoded body (for POST, used by OAuth token exchange)
        timeout: Request timeout in seconds
        retries: Number of retries on failure
        raw: Return raw bytes instead of parsed JSON

    Returns:
        Parsed JSON response, raw text (if raw=True)
    """
    headers = dict(headers or {})
    headers.setdefault("User-Agent", USER_AGENT)

    data = None
    if json_data is not None:
        data = json.dumps(json_data).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    elif form_data is not None:
        data = urlencode(form_data).encode("utf-8")
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    log(f"{method} {url}")

    last_error = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read()
                log(f"Response: {response.status} ({len(body)} bytes)")
                if raw:
                    return body
                text = body.decode("utf-8")
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as e:
            body_text = None
            try:
                body_text = e.read().decode("utf-8")
            except Exception:
                pass
            log(f"HTTP Error {e.code}: {e.reason}")
            if body_text:
                log(f"Error body: {body_text[:300]}")
            last_error = HTTPError(f"HTTP {e.code}: {e.reason}", e.code, body_text)

            # Don't retry client errors (4xx) except rate limits
            if 400 <= e.code < 500 and e.code != 429:
                raise last_error

            if attempt < retries - 1:
                delay = RETRY_DELAY * (2 ** attempt)
                if e.code == 429:
                    retry_after = e.headers.get("Retry-After") if hasattr(e, "headers") else None
                    if retry_after:
                        try:
                            delay = float(retry_after)
                        except ValueError:
                            pass
                    delay = max(delay, 3.0)
                time.sleep(delay)
        except urllib.error.URLError as e:
            log(f"URL Error: {e.reason}")
            last_error = HTTPError(f"URL Error: {e.reason}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
        except json.JSONDecodeError as e:
            log(f"JSON decode error: {e}")
            last_error = HTTPError(f"Invalid JSON response: {e}")
            raise last_error
        except (OSError, TimeoutError, ConnectionResetError) as e:
            log(f"Connection error: {type(e).__name__}: {e}")
            last_error = HTTPError(f"Connection error: {type(e).__name__}: {e}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))

    if last_error:
        raise last_error
    raise HTTPError("Request failed with no error details")


def get(url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
    """Make a GET request."""
    return request("GET", url, headers=headers, **kwargs)


def post(url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
    """Make a POST request."""
    return request("POST", url, headers=headers, **kwargs)
