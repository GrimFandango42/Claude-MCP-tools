"""Epic FHIR endpoint registry and SMART on FHIR discovery.

Bundles known Epic endpoints for major health systems + sandbox.
Discovers OAuth endpoints via .well-known/smart-configuration.
"""

import json
import sys
from typing import Any, Dict, Optional, Tuple

from . import http

# Epic sandbox for testing (no app registration needed)
EPIC_SANDBOX = {
    "name": "Epic Sandbox (Test)",
    "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    "client_id": "6c12dff4-24e7-4475-a742-b08972c4571d",  # Epic public sandbox client
}

# Known Epic FHIR endpoints (subset — Epic publishes full list at open.epic.com/MyApps/Endpoints)
KNOWN_ENDPOINTS: Dict[str, Dict[str, str]] = {
    "epic sandbox": {
        "name": "Epic Sandbox (Test)",
        "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    },
    # Major health systems — user can also provide a FHIR URL directly
    "kaiser permanente": {
        "name": "Kaiser Permanente",
        "fhir_base_url": "https://epicfhir.kaiser.org/PF-FHIR-PROXY/api/FHIR/R4",
    },
    "mayo clinic": {
        "name": "Mayo Clinic",
        "fhir_base_url": "https://fhir.mayoclinic.org/FHIR/api/FHIR/R4",
    },
    "cleveland clinic": {
        "name": "Cleveland Clinic",
        "fhir_base_url": "https://epicproxy.clevelandclinic.org/FHIR/api/FHIR/R4",
    },
    "johns hopkins": {
        "name": "Johns Hopkins Medicine",
        "fhir_base_url": "https://epicfhir.johnshopkins.edu/FHIR/api/FHIR/R4",
    },
    "duke health": {
        "name": "Duke Health",
        "fhir_base_url": "https://health-apis.duke.edu/FHIR/api/FHIR/R4",
    },
    "mount sinai": {
        "name": "Mount Sinai Health System",
        "fhir_base_url": "https://epicfhir.mountsinai.org/FHIR-PRD/api/FHIR/R4",
    },
    "stanford health": {
        "name": "Stanford Health Care",
        "fhir_base_url": "https://epicfhir.stanfordhealthcare.org/FHIR/api/FHIR/R4",
    },
    "uchealth": {
        "name": "UCHealth",
        "fhir_base_url": "https://fhir.uchealth.org/FHIR/api/FHIR/R4",
    },
    "yale new haven": {
        "name": "Yale New Haven Health",
        "fhir_base_url": "https://epicfhir.ynhhs.org/FHIR/api/FHIR/R4",
    },
}


def lookup_endpoint(name: str) -> Optional[Dict[str, str]]:
    """Look up a known endpoint by name (case-insensitive fuzzy match)."""
    name_lower = name.lower().strip()

    # Exact match
    if name_lower in KNOWN_ENDPOINTS:
        return KNOWN_ENDPOINTS[name_lower]

    # Substring match
    for key, ep in KNOWN_ENDPOINTS.items():
        if name_lower in key or name_lower in ep["name"].lower():
            return ep

    return None


def discover_smart_config(fhir_base_url: str) -> Dict[str, str]:
    """Discover OAuth endpoints via SMART on FHIR .well-known/smart-configuration.

    Returns dict with 'authorization_endpoint' and 'token_endpoint'.
    Falls back to /metadata CapabilityStatement if .well-known fails.
    """
    base = fhir_base_url.rstrip("/")

    # Try .well-known/smart-configuration first
    try:
        config = http.get(f"{base}/.well-known/smart-configuration")
        result = {}
        if "authorization_endpoint" in config:
            result["authorization_endpoint"] = config["authorization_endpoint"]
        if "token_endpoint" in config:
            result["token_endpoint"] = config["token_endpoint"]
        if result.get("authorization_endpoint") and result.get("token_endpoint"):
            http.log(f"SMART config discovered: {result}")
            return result
    except http.HTTPError:
        http.log("No .well-known/smart-configuration, trying /metadata")

    # Fallback: parse CapabilityStatement
    try:
        metadata = http.get(
            f"{base}/metadata",
            headers={"Accept": "application/fhir+json"},
        )
        for rest in metadata.get("rest", []):
            security = rest.get("security", {})
            for ext in security.get("extension", []):
                if ext.get("url") == "http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris":
                    result = {}
                    for sub in ext.get("extension", []):
                        if sub.get("url") == "authorize":
                            result["authorization_endpoint"] = sub["valueUri"]
                        elif sub.get("url") == "token":
                            result["token_endpoint"] = sub["valueUri"]
                    if result.get("authorization_endpoint") and result.get("token_endpoint"):
                        return result
    except http.HTTPError as e:
        http.log(f"Metadata fetch failed: {e}")

    raise ValueError(
        f"Could not discover OAuth endpoints for {fhir_base_url}. "
        "Ensure this is a valid FHIR R4 endpoint with SMART on FHIR support."
    )


def resolve_org(
    name_or_url: str, client_id: Optional[str] = None, sandbox: bool = False
) -> Dict[str, str]:
    """Resolve an organization name or FHIR URL to full connection info.

    Returns dict with: name, fhir_base_url, authorize_url, token_url, client_id
    """
    import os

    if sandbox:
        fhir_base_url = EPIC_SANDBOX["fhir_base_url"]
        name = EPIC_SANDBOX["name"]
        cid = EPIC_SANDBOX["client_id"]
    elif name_or_url.startswith("http"):
        fhir_base_url = name_or_url.rstrip("/")
        name = fhir_base_url.split("//")[1].split("/")[0]
        cid = client_id or os.environ.get("EPIC_CLIENT_ID", "")
    else:
        ep = lookup_endpoint(name_or_url)
        if not ep:
            raise ValueError(
                f"Unknown organization: '{name_or_url}'. "
                "Use --fhir-url to provide the FHIR endpoint directly, "
                "or try a different name. Known orgs: "
                + ", ".join(sorted(KNOWN_ENDPOINTS.keys()))
            )
        fhir_base_url = ep["fhir_base_url"]
        name = ep["name"]
        cid = client_id or os.environ.get("EPIC_CLIENT_ID", "")

    if not cid:
        raise ValueError(
            "No client_id available. Set EPIC_CLIENT_ID env var, "
            "or use --sandbox for testing, or pass --client-id."
        )

    # Discover OAuth endpoints
    smart = discover_smart_config(fhir_base_url)

    return {
        "name": name,
        "fhir_base_url": fhir_base_url,
        "authorize_url": smart["authorization_endpoint"],
        "token_url": smart["token_endpoint"],
        "client_id": cid,
    }
