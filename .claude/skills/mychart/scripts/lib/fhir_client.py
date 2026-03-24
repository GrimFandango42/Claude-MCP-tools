"""FHIR R4 API client for Epic MyChart.

Handles read, search, and create operations with:
- Bundle pagination (follow next links)
- OperationOutcome error parsing
- Auto token refresh on 401
- Patient compartment scoping
"""

import json
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urljoin

from . import http
from . import token_store


class FHIRError(Exception):
    """FHIR-specific error with OperationOutcome details."""

    def __init__(self, message: str, status_code: Optional[int] = None, issues: Optional[List[Dict]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.issues = issues or []


def _parse_operation_outcome(body: Optional[str]) -> Optional[List[Dict]]:
    """Parse FHIR OperationOutcome from error response body."""
    if not body:
        return None
    try:
        data = json.loads(body)
        if data.get("resourceType") == "OperationOutcome":
            return [
                {
                    "severity": i.get("severity", ""),
                    "code": i.get("code", ""),
                    "diagnostics": i.get("diagnostics", ""),
                    "details": i.get("details", {}).get("text", ""),
                }
                for i in data.get("issue", [])
            ]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


class FHIRClient:
    """FHIR R4 client for patient-authorized access."""

    def __init__(self, fhir_base_url: str, access_token: str, patient_id: Optional[str] = None):
        self.base_url = fhir_base_url.rstrip("/")
        self.access_token = access_token
        self.patient_id = patient_id

    def _headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/fhir+json",
            "Authorization": f"Bearer {self.access_token}",
        }

    def _request(self, method: str, url: str, json_data: Optional[Dict] = None) -> Dict:
        """Make a FHIR request with error handling."""
        try:
            kwargs = {"headers": self._headers(), "retries": 2}
            if json_data:
                kwargs["json_data"] = json_data
            return http.request(method, url, **kwargs)
        except http.HTTPError as e:
            issues = _parse_operation_outcome(e.body)
            if issues:
                details = "; ".join(
                    i.get("diagnostics") or i.get("details") or i.get("code", "")
                    for i in issues
                )
                raise FHIRError(
                    f"FHIR error ({e.status_code}): {details}",
                    status_code=e.status_code,
                    issues=issues,
                )
            raise FHIRError(str(e), status_code=e.status_code)

    def read(self, resource_type: str, resource_id: str) -> Dict:
        """Read a single FHIR resource by type and ID.

        GET {base}/{type}/{id}
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}"
        return self._request("GET", url)

    def search(
        self,
        resource_type: str,
        params: Optional[Dict[str, str]] = None,
        max_pages: int = 5,
    ) -> List[Dict]:
        """Search for FHIR resources with pagination.

        GET {base}/{type}?{params}
        Returns list of matching resources (unwrapped from Bundle).
        """
        params = dict(params or {})

        # Scope to patient if we have a patient ID
        if self.patient_id and resource_type != "Patient":
            params.setdefault("patient", self.patient_id)

        query = urlencode(params) if params else ""
        url = f"{self.base_url}/{resource_type}"
        if query:
            url = f"{url}?{query}"

        resources = []
        pages_fetched = 0

        while url and pages_fetched < max_pages:
            bundle = self._request("GET", url)

            if bundle.get("resourceType") != "Bundle":
                # Single resource returned
                resources.append(bundle)
                break

            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                if resource:
                    resources.append(resource)

            # Follow next link for pagination
            url = None
            for link in bundle.get("link", []):
                if link.get("relation") == "next":
                    url = link.get("url")
                    break

            pages_fetched += 1

        return resources

    def create(self, resource_type: str, resource: Dict) -> Dict:
        """Create a new FHIR resource.

        POST {base}/{type}
        """
        url = f"{self.base_url}/{resource_type}"
        return self._request("POST", url, json_data=resource)

    def get_patient(self) -> Dict:
        """Get the authenticated patient's record."""
        if self.patient_id:
            return self.read("Patient", self.patient_id)
        # Search for self
        results = self.search("Patient", {"_id": self.patient_id} if self.patient_id else {})
        if results:
            return results[0]
        raise FHIRError("Could not find patient record")


def get_client(org_id: Optional[int] = None) -> FHIRClient:
    """Get a FHIRClient with valid token for the specified (or default) org.

    Handles token refresh automatically. Raises if no valid token available.
    """
    token = token_store.get_token(org_id)
    if not token:
        org = token_store.get_default_org()
        org_name = org["name"] if org else "any organization"
        raise FHIRError(
            f"Not connected to {org_name}. Run: /mychart connect"
        )

    # Check if token needs refresh
    if token_store.is_token_expired(token):
        if token.get("refresh_token"):
            # Try to refresh
            try:
                new_token = _refresh_token(token)
                token = new_token
            except Exception as e:
                raise FHIRError(
                    f"Token expired and refresh failed: {e}. Run: /mychart connect"
                )
        else:
            raise FHIRError(
                "Token expired (no refresh token). Run: /mychart connect"
            )

    return FHIRClient(
        fhir_base_url=token["fhir_base_url"],
        access_token=token["access_token"],
        patient_id=token.get("patient_id"),
    )


def _refresh_token(token: Dict) -> Dict:
    """Refresh an expired access token."""
    from datetime import datetime, timedelta

    resp = http.post(
        token["token_url"],
        form_data={
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
            "client_id": token["client_id"],
        },
    )

    expires_in = resp.get("expires_in", 3600)
    expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()

    token_store.store_tokens(
        org_id=token["org_id"],
        access_token=resp["access_token"],
        refresh_token=resp.get("refresh_token", token["refresh_token"]),
        expires_at=expires_at,
        scope=resp.get("scope", token.get("scope")),
        patient_id=resp.get("patient", token.get("patient_id")),
    )

    # Return updated token dict
    updated = dict(token)
    updated["access_token"] = resp["access_token"]
    updated["expires_at"] = expires_at
    if resp.get("refresh_token"):
        updated["refresh_token"] = resp["refresh_token"]
    return updated
