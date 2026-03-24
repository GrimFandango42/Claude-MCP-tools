#!/usr/bin/env python3
"""OAuth2 + PKCE authentication for Epic MyChart FHIR.

Supports two modes:
1. Localhost callback (default) — starts local server, opens browser
2. Manual paste (--manual or fallback) — user copies auth code from browser

Usage:
    python3 auth.py connect "Kaiser Permanente"
    python3 auth.py connect --sandbox
    python3 auth.py connect --fhir-url https://epicfhir.example.org/FHIR/api/FHIR/R4
    python3 auth.py connect --manual "Hospital Name"
    python3 auth.py status
    python3 auth.py refresh --org-id 1
"""

import argparse
import base64
import hashlib
import json
import os
import secrets
import socket
import sys
import threading
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from datetime import datetime, timedelta

# Add lib to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib import http
from lib import token_store
from lib import endpoints

CALLBACK_PORT_START = 9876
CALLBACK_PORT_END = 9886
DEFAULT_SCOPES = "openid fhirUser patient/*.read launch/patient"


def _generate_pkce() -> tuple:
    """Generate PKCE code_verifier and code_challenge."""
    # code_verifier: 43-128 chars, unreserved charset
    verifier = secrets.token_urlsafe(64)[:128]
    # code_challenge: SHA256(verifier), base64url-encoded, no padding
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    return verifier, challenge


def _find_open_port() -> int:
    """Find an available port in range."""
    for port in range(CALLBACK_PORT_START, CALLBACK_PORT_END + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("127.0.0.1", port))
            sock.close()
            return port
        except OSError:
            continue
    raise RuntimeError(f"No open ports in range {CALLBACK_PORT_START}-{CALLBACK_PORT_END}")


class _CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler that captures the OAuth callback."""

    auth_code = None
    auth_state = None
    auth_error = None

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/callback":
            if "error" in params:
                _CallbackHandler.auth_error = params["error"][0]
                error_desc = params.get("error_description", [""])[0]
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    f"<html><body><h2>Authentication Failed</h2>"
                    f"<p>{_CallbackHandler.auth_error}: {error_desc}</p>"
                    f"<p>You can close this window.</p></body></html>".encode()
                )
            elif "code" in params:
                _CallbackHandler.auth_code = params["code"][0]
                _CallbackHandler.auth_state = params.get("state", [None])[0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h2>Authentication Successful!</h2>"
                    b"<p>You can close this window and return to Claude.</p></body></html>"
                )
            else:
                self.send_response(400)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Missing authorization code")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress request logging (goes to stderr otherwise)."""
        pass


def _exchange_code(
    token_url: str,
    code: str,
    redirect_uri: str,
    client_id: str,
    code_verifier: str,
) -> dict:
    """Exchange authorization code for tokens."""
    return http.post(
        token_url,
        form_data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "code_verifier": code_verifier,
        },
    )


def cmd_connect(args):
    """Connect to a health system via OAuth2 + PKCE."""
    # Resolve organization
    name_or_url = args.org or ""
    if args.fhir_url:
        name_or_url = args.fhir_url

    try:
        org_info = endpoints.resolve_org(
            name_or_url,
            client_id=args.client_id,
            sandbox=args.sandbox,
        )
    except ValueError as e:
        print(json.dumps({"status": "error", "error": str(e)}))
        sys.exit(1)

    # Register org in DB
    org_id = token_store.add_org(
        name=org_info["name"],
        fhir_base_url=org_info["fhir_base_url"],
        authorize_url=org_info["authorize_url"],
        token_url=org_info["token_url"],
        client_id=org_info["client_id"],
    )

    # Generate PKCE
    code_verifier, code_challenge = _generate_pkce()
    state = secrets.token_hex(32)

    # Store state for verification
    token_store.store_auth_state(state, code_verifier, org_id)

    scopes = args.scopes or DEFAULT_SCOPES

    # Determine auth mode
    use_manual = args.manual
    port = None
    redirect_uri = None

    if not use_manual:
        try:
            port = _find_open_port()
            redirect_uri = f"http://localhost:{port}/callback"
        except RuntimeError:
            sys.stderr.write("[mychart] No open port available, falling back to manual mode\n")
            use_manual = True

    if use_manual:
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

    # Build authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": org_info["client_id"],
        "redirect_uri": redirect_uri,
        "scope": scopes,
        "state": state,
        "aud": org_info["fhir_base_url"],
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{org_info['authorize_url']}?{urlencode(auth_params)}"

    if use_manual:
        # Manual mode: print URL, wait for code paste
        print(json.dumps({
            "status": "awaiting_auth",
            "mode": "manual",
            "org": org_info["name"],
            "auth_url": auth_url,
            "instructions": (
                "Open the URL above in your browser, sign in with MyChart, "
                "then paste the authorization code here."
            ),
        }))

        # Read code from stdin
        sys.stderr.write("\nPaste authorization code: ")
        sys.stderr.flush()
        code = input().strip()

        if not code:
            print(json.dumps({"status": "error", "error": "No authorization code provided"}))
            sys.exit(1)

    else:
        # Localhost callback mode
        print(json.dumps({
            "status": "awaiting_auth",
            "mode": "localhost",
            "org": org_info["name"],
            "auth_url": auth_url,
            "port": port,
            "instructions": (
                f"Opening browser for MyChart sign-in. "
                f"If the browser doesn't open, visit the auth_url manually."
            ),
        }))
        sys.stdout.flush()

        # Start local server
        server = HTTPServer(("127.0.0.1", port), _CallbackHandler)
        server.timeout = 300  # 5 minute timeout

        # Try to open browser
        try:
            webbrowser.open(auth_url)
        except Exception:
            pass

        # Wait for callback
        _CallbackHandler.auth_code = None
        _CallbackHandler.auth_error = None

        while _CallbackHandler.auth_code is None and _CallbackHandler.auth_error is None:
            server.handle_request()

        server.server_close()

        if _CallbackHandler.auth_error:
            print(json.dumps({
                "status": "error",
                "error": f"Authentication failed: {_CallbackHandler.auth_error}",
            }))
            sys.exit(1)

        code = _CallbackHandler.auth_code

        # Verify state
        if _CallbackHandler.auth_state != state:
            print(json.dumps({
                "status": "error",
                "error": "State mismatch — possible CSRF attack. Try again.",
            }))
            sys.exit(1)

    # Exchange code for tokens
    try:
        token_resp = _exchange_code(
            token_url=org_info["token_url"],
            code=code,
            redirect_uri=redirect_uri,
            client_id=org_info["client_id"],
            code_verifier=code_verifier,
        )
    except http.HTTPError as e:
        print(json.dumps({"status": "error", "error": f"Token exchange failed: {e}"}))
        sys.exit(1)

    # Calculate expiry
    expires_in = token_resp.get("expires_in", 3600)
    expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()

    # Store tokens
    token_store.store_tokens(
        org_id=org_id,
        access_token=token_resp["access_token"],
        refresh_token=token_resp.get("refresh_token"),
        expires_at=expires_at,
        scope=token_resp.get("scope", scopes),
        patient_id=token_resp.get("patient"),
        id_token=token_resp.get("id_token"),
    )

    print(json.dumps({
        "status": "connected",
        "org": org_info["name"],
        "patient_id": token_resp.get("patient", ""),
        "scopes": token_resp.get("scope", scopes),
        "expires_at": expires_at,
    }))


def cmd_status(args):
    """Check token status for all connected orgs."""
    orgs = token_store.list_orgs()
    if not orgs:
        print(json.dumps({"status": "no_orgs", "message": "No organizations connected. Run: /mychart connect"}))
        return

    results = []
    for org in orgs:
        token = token_store.get_token(org["id"])
        if token:
            expired = token_store.is_token_expired(token, buffer_seconds=0)
            refreshable = bool(token.get("refresh_token"))
            results.append({
                "org": org["name"],
                "org_id": org["id"],
                "default": bool(org["is_default"]),
                "patient_id": token.get("patient_id", ""),
                "expired": expired,
                "refreshable": refreshable,
                "expires_at": token.get("expires_at", ""),
                "scope": token.get("scope", ""),
            })
        else:
            results.append({
                "org": org["name"],
                "org_id": org["id"],
                "default": bool(org["is_default"]),
                "expired": True,
                "refreshable": False,
                "message": "No token stored",
            })

    print(json.dumps({"status": "ok", "organizations": results}))


def cmd_refresh(args):
    """Refresh token for an org."""
    token = token_store.get_token(args.org_id)
    if not token:
        print(json.dumps({"status": "error", "error": "No token found for this org"}))
        sys.exit(1)

    if not token.get("refresh_token"):
        print(json.dumps({"status": "error", "error": "No refresh token. Re-authenticate with: /mychart connect"}))
        sys.exit(1)

    try:
        from lib.fhir_client import _refresh_token
        _refresh_token(token)
        print(json.dumps({"status": "refreshed", "org_id": args.org_id}))
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="MyChart OAuth2 authentication")
    subparsers = parser.add_subparsers(dest="command")

    # connect
    p_connect = subparsers.add_parser("connect", help="Connect to a health system")
    p_connect.add_argument("org", nargs="?", help="Organization name (e.g., 'Kaiser Permanente')")
    p_connect.add_argument("--sandbox", action="store_true", help="Use Epic sandbox for testing")
    p_connect.add_argument("--fhir-url", help="Direct FHIR base URL")
    p_connect.add_argument("--client-id", help="Override client_id")
    p_connect.add_argument("--scopes", help="Override OAuth scopes")
    p_connect.add_argument("--manual", action="store_true", help="Manual auth code paste mode")

    # status
    subparsers.add_parser("status", help="Check connection status")

    # refresh
    p_refresh = subparsers.add_parser("refresh", help="Refresh token")
    p_refresh.add_argument("--org-id", type=int, required=True, help="Organization ID")

    args = parser.parse_args()

    if args.command == "connect":
        cmd_connect(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "refresh":
        cmd_refresh(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
