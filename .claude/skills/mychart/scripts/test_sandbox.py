#!/usr/bin/env python3
"""Epic FHIR sandbox test harness.

Registers Epic's open sandbox, runs all data modes, and reports results.

Usage:
    python3 test_sandbox.py setup [--client-id ID]
    python3 test_sandbox.py test [--org-id N]
    python3 test_sandbox.py smoke [--org-id N]
    python3 test_sandbox.py scopes [--org-id N]
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add script dir to path for lib imports (same pattern as mychart.py)
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib import http
from lib import token_store
from lib import endpoints
from lib.fhir_client import FHIRClient, FHIRError, get_client

# --- Constants ---

SANDBOX_NAME = "Epic Sandbox (Test)"
SANDBOX_FHIR_BASE = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
SANDBOX_AUTH_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize"
SANDBOX_TOKEN_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
DEFAULT_SANDBOX_CLIENT_ID = "2a76a53d-28f6-4e2e-863d-0ac07e3a3b47"

# All 23 data modes from mychart.py that require FHIR access
ALL_MODES: List[Dict[str, Any]] = [
    {"name": "patient",        "resource": "Patient",              "params": {},                                                    "method": "read"},
    {"name": "labs",           "resource": "Observation",          "params": {"category": "laboratory", "_sort": "-date", "_count": "5"}},
    {"name": "vitals",         "resource": "Observation",          "params": {"category": "vital-signs", "_sort": "-date", "_count": "5"}},
    {"name": "meds",           "resource": "MedicationRequest",    "params": {"_sort": "-authoredon", "_count": "5"}},
    {"name": "conditions",     "resource": "Condition",            "params": {"_count": "5"}},
    {"name": "allergies",      "resource": "AllergyIntolerance",   "params": {"_count": "5"}},
    {"name": "immunizations",  "resource": "Immunization",         "params": {"_sort": "-date", "_count": "5"}},
    {"name": "appointments",   "resource": "Appointment",          "params": {"_sort": "date", "_count": "5"}},
    {"name": "procedures",     "resource": "Procedure",            "params": {"_sort": "-date", "_count": "5"}},
    {"name": "encounters",     "resource": "Encounter",            "params": {"_sort": "-date", "_count": "5"}},
    {"name": "documents",      "resource": "DocumentReference",    "params": {"_sort": "-date", "_count": "5"}},
    {"name": "coverage",       "resource": "Coverage",             "params": {"_count": "5"}},
    {"name": "careplans",      "resource": "CarePlan",             "params": {"_count": "5"}},
    {"name": "goals",          "resource": "Goal",                 "params": {"_count": "5"}},
    {"name": "familyhistory",  "resource": "FamilyMemberHistory",  "params": {"_count": "5"}},
    {"name": "diagnostics",    "resource": "DiagnosticReport",     "params": {"_sort": "-date", "_count": "5"}},
    {"name": "everything",     "resource": "Patient",              "params": {},                                                    "method": "everything"},
    {"name": "lastn-vitals",   "resource": "Observation",          "params": {"category": "vital-signs"},                           "method": "lastn"},
    {"name": "lastn-labs",     "resource": "Observation",          "params": {"category": "laboratory"},                            "method": "lastn"},
    {"name": "search-condition",   "resource": "Condition",        "params": {"_count": "3"}},
    {"name": "search-medication",  "resource": "MedicationRequest","params": {"_count": "3"}},
    {"name": "search-observation", "resource": "Observation",      "params": {"_count": "3"}},
    {"name": "summary",        "resource": None,                   "params": {},                                                    "method": "summary"},
]

SMOKE_MODES = {"patient", "labs", "meds", "conditions", "vitals"}

# FHIR scope -> modes mapping
SCOPE_MODE_MAP = {
    "patient/Patient.read":              ["patient", "summary"],
    "patient/Observation.read":          ["labs", "vitals", "lastn-vitals", "lastn-labs", "search-observation"],
    "patient/MedicationRequest.read":    ["meds", "search-medication"],
    "patient/Condition.read":            ["conditions", "search-condition"],
    "patient/AllergyIntolerance.read":   ["allergies"],
    "patient/Immunization.read":         ["immunizations"],
    "patient/Appointment.read":          ["appointments"],
    "patient/Procedure.read":            ["procedures"],
    "patient/Encounter.read":            ["encounters"],
    "patient/DocumentReference.read":    ["documents"],
    "patient/Coverage.read":             ["coverage"],
    "patient/CarePlan.read":             ["careplans"],
    "patient/Goal.read":                 ["goals"],
    "patient/FamilyMemberHistory.read":  ["familyhistory"],
    "patient/DiagnosticReport.read":     ["diagnostics"],
    "patient/*.read":                    ["all"],
}


# --- Result types ---

class TestResult:
    """Outcome for a single mode test."""

    def __init__(self, mode: str, status: str, count: int = 0,
                 elapsed_ms: float = 0.0, error: str = "", http_code: int = 0):
        self.mode = mode
        self.status = status       # "ok", "empty", "forbidden", "error"
        self.count = count
        self.elapsed_ms = elapsed_ms
        self.error = error
        self.http_code = http_code

    def to_dict(self) -> dict:
        d = {"mode": self.mode, "status": self.status, "elapsed_ms": round(self.elapsed_ms, 1)}
        if self.count:
            d["count"] = self.count
        if self.error:
            d["error"] = self.error
        if self.http_code:
            d["http_code"] = self.http_code
        return d


# --- Mode execution ---

def _run_summary(client: FHIRClient) -> Tuple[int, str]:
    """Run the summary mode (multi-resource fetch). Returns (total_count, error)."""
    fetches = [
        ("Patient",              {"_id": client.patient_id} if client.patient_id else {}),
        ("Condition",            {"clinical-status": "active", "_count": "10"}),
        ("AllergyIntolerance",   {"clinical-status": "active", "_count": "10"}),
        ("MedicationRequest",    {"status": "active", "_count": "10"}),
        ("Observation",          {"category": "laboratory", "_sort": "-date", "_count": "5"}),
        ("Observation",          {"category": "vital-signs", "_sort": "-date", "_count": "5"}),
        ("Immunization",         {"_sort": "-date", "_count": "5"}),
        ("Coverage",             {"status": "active", "_count": "5"}),
    ]
    total = 0
    errors = []
    for rtype, params in fetches:
        try:
            results = client.search(rtype, params)
            total += len(results)
        except FHIRError as e:
            errors.append(f"{rtype}: {e}")
    error_str = "; ".join(errors) if errors else ""
    return total, error_str


def run_mode(client: FHIRClient, mode_def: Dict[str, Any]) -> TestResult:
    """Execute a single mode against the sandbox and return a TestResult."""
    name = mode_def["name"]
    method = mode_def.get("method", "search")

    t0 = time.monotonic()
    try:
        if method == "read" and name == "patient":
            result = client.get_patient()
            count = 1 if result else 0
            elapsed = (time.monotonic() - t0) * 1000
            return TestResult(name, "ok" if count else "empty", count=count, elapsed_ms=elapsed)

        elif method == "everything":
            results = client.everything()
            elapsed = (time.monotonic() - t0) * 1000
            count = len(results)
            return TestResult(name, "ok" if count else "empty", count=count, elapsed_ms=elapsed)

        elif method == "lastn":
            category = mode_def["params"].get("category", "vital-signs")
            results = client.lastn(category=category, max_per_code=1)
            elapsed = (time.monotonic() - t0) * 1000
            count = len(results)
            return TestResult(name, "ok" if count else "empty", count=count, elapsed_ms=elapsed)

        elif method == "summary":
            total, error_str = _run_summary(client)
            elapsed = (time.monotonic() - t0) * 1000
            status = "ok" if total else ("error" if error_str else "empty")
            return TestResult(name, status, count=total, elapsed_ms=elapsed,
                              error=error_str if error_str else "")

        else:
            # Standard search
            results = client.search(mode_def["resource"], mode_def["params"])
            elapsed = (time.monotonic() - t0) * 1000
            count = len(results)
            return TestResult(name, "ok" if count else "empty", count=count, elapsed_ms=elapsed)

    except FHIRError as e:
        elapsed = (time.monotonic() - t0) * 1000
        code = e.status_code or 0
        if code == 403:
            return TestResult(name, "forbidden", elapsed_ms=elapsed, error=str(e), http_code=code)
        elif code == 401:
            return TestResult(name, "error", elapsed_ms=elapsed,
                              error="Token expired or invalid (401)", http_code=code)
        else:
            return TestResult(name, "error", elapsed_ms=elapsed, error=str(e), http_code=code)
    except Exception as e:
        elapsed = (time.monotonic() - t0) * 1000
        return TestResult(name, "error", elapsed_ms=elapsed, error=f"{type(e).__name__}: {e}")


# --- Output formatting ---

def _status_symbol(status: str) -> str:
    """ASCII status indicator."""
    return {
        "ok":        "[PASS]",
        "empty":     "[ OK ]",
        "forbidden": "[DENY]",
        "error":     "[FAIL]",
    }.get(status, "[????]")


def print_summary_table(results: List[TestResult]) -> None:
    """Print a formatted summary table to stdout."""
    ok      = [r for r in results if r.status == "ok"]
    empty   = [r for r in results if r.status == "empty"]
    denied  = [r for r in results if r.status == "forbidden"]
    errors  = [r for r in results if r.status == "error"]

    total_ms = sum(r.elapsed_ms for r in results)
    sep = "-" * 78

    print(f"\n{sep}")
    print(f"  EPIC SANDBOX TEST RESULTS  ({datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')})")
    print(sep)
    print(f"  {'Mode':<24} {'Status':<10} {'Count':>6} {'Time (ms)':>10}  Notes")
    print(sep)

    for r in results:
        sym = _status_symbol(r.status)
        note = ""
        if r.error and r.status != "forbidden":
            # Truncate long errors for table display
            note = r.error[:40] + "..." if len(r.error) > 40 else r.error
        elif r.status == "forbidden":
            note = f"HTTP {r.http_code}" if r.http_code else "scope denied"
        print(f"  {r.mode:<24} {sym:<10} {r.count:>6} {r.elapsed_ms:>10.1f}  {note}")

    print(sep)
    print(f"  Passed with data : {len(ok):>3}")
    print(f"  Passed (empty)   : {len(empty):>3}")
    print(f"  Forbidden (403)  : {len(denied):>3}")
    print(f"  Errors           : {len(errors):>3}")
    print(f"  Total modes      : {len(results):>3}")
    print(f"  Total time       : {total_ms:>7.0f} ms")
    print(sep)

    # Also emit machine-readable JSON to stderr for programmatic consumers
    summary_json = {
        "total": len(results),
        "passed_with_data": len(ok),
        "passed_empty": len(empty),
        "forbidden": len(denied),
        "errors": len(errors),
        "total_ms": round(total_ms, 1),
        "results": [r.to_dict() for r in results],
    }
    sys.stderr.write(json.dumps(summary_json) + "\n")


# --- Commands ---

def cmd_setup(args):
    """Register Epic's open FHIR sandbox as an org."""
    client_id = args.client_id or DEFAULT_SANDBOX_CLIENT_ID

    # Register directly with known URLs (sandbox .well-known can be flaky)
    org_id = token_store.add_org(
        name=SANDBOX_NAME,
        fhir_base_url=SANDBOX_FHIR_BASE,
        authorize_url=SANDBOX_AUTH_URL,
        token_url=SANDBOX_TOKEN_URL,
        client_id=client_id,
        set_default=True,
    )

    result = {
        "status": "ok",
        "action": "sandbox_registered",
        "org_id": org_id,
        "name": SANDBOX_NAME,
        "fhir_base_url": SANDBOX_FHIR_BASE,
        "authorize_url": SANDBOX_AUTH_URL,
        "token_url": SANDBOX_TOKEN_URL,
        "client_id": client_id,
        "next_step": (
            "Sandbox org registered and set as default. "
            "Run `python3 auth.py connect --sandbox` to authenticate, "
            "then `python3 test_sandbox.py test` to run all modes."
        ),
    }
    print(json.dumps(result, indent=2))


def cmd_test(args):
    """Run ALL 23 data modes against the sandbox."""
    client = _get_test_client(args)
    modes = ALL_MODES

    print(f"Running {len(modes)} modes against Epic sandbox...\n")
    results = []
    for i, mode_def in enumerate(modes, 1):
        name = mode_def["name"]
        sys.stderr.write(f"  [{i:>2}/{len(modes)}] {name:<24}")
        sys.stderr.flush()

        result = run_mode(client, mode_def)
        results.append(result)

        sym = _status_symbol(result.status)
        sys.stderr.write(f" {sym}  {result.elapsed_ms:>7.1f} ms")
        if result.count:
            sys.stderr.write(f"  ({result.count} resources)")
        sys.stderr.write("\n")
        sys.stderr.flush()

    print_summary_table(results)


def cmd_smoke(args):
    """Quick 5-mode smoke test: patient, labs, meds, conditions, vitals."""
    client = _get_test_client(args)
    smoke_defs = [m for m in ALL_MODES if m["name"] in SMOKE_MODES]

    print(f"Running smoke test ({len(smoke_defs)} modes)...\n")
    results = []
    for i, mode_def in enumerate(smoke_defs, 1):
        name = mode_def["name"]
        sys.stderr.write(f"  [{i}/{len(smoke_defs)}] {name:<24}")
        sys.stderr.flush()

        result = run_mode(client, mode_def)
        results.append(result)

        sym = _status_symbol(result.status)
        sys.stderr.write(f" {sym}  {result.elapsed_ms:>7.1f} ms")
        if result.count:
            sys.stderr.write(f"  ({result.count} resources)")
        sys.stderr.write("\n")
        sys.stderr.flush()

    print_summary_table(results)


def cmd_scopes(args):
    """Read stored token and map granted scopes to available modes."""
    org_id = getattr(args, "org_id", None)
    token = token_store.get_token(org_id)

    if not token:
        print(json.dumps({
            "status": "error",
            "error": "No token found. Run auth.py connect --sandbox first.",
        }))
        sys.exit(1)

    scope_str = token.get("scope", "")
    granted = set(scope_str.split()) if scope_str else set()

    # Check expiry
    expired = token_store.is_token_expired(token, buffer_seconds=0)

    # Map scopes to modes
    has_wildcard = "patient/*.read" in granted
    covered_modes = set()
    scope_details = []

    for scope, modes in SCOPE_MODE_MAP.items():
        is_granted = scope in granted or has_wildcard
        if "all" in modes:
            # Wildcard scope -- covers everything
            if is_granted:
                covered_modes = {m["name"] for m in ALL_MODES}
        else:
            if is_granted:
                covered_modes.update(modes)
        scope_details.append({
            "scope": scope,
            "granted": is_granted,
            "modes": modes if "all" not in modes else ["(all modes)"],
        })

    all_mode_names = [m["name"] for m in ALL_MODES]
    uncovered = [m for m in all_mode_names if m not in covered_modes]

    # Print human-readable table
    sep = "-" * 60
    print(f"\n{sep}")
    print("  GRANTED SCOPES AND MODE COVERAGE")
    print(sep)
    print(f"\n  Token for: {token.get('org_name', 'Unknown')}")
    print(f"  Patient:   {token.get('patient_id', 'N/A')}")
    print(f"  Expired:   {'YES' if expired else 'No'}")
    print(f"  Expires:   {token.get('expires_at', 'N/A')}")
    print(f"\n  Raw scopes: {scope_str or '(none)'}\n")

    print(f"  {'Scope':<42} {'Granted':>8}")
    print(f"  {'-'*42} {'-'*8}")
    for sd in scope_details:
        mark = "  YES" if sd["granted"] else "   --"
        print(f"  {sd['scope']:<42} {mark:>8}")

    print(f"\n  Modes covered: {len(covered_modes)}/{len(all_mode_names)}")
    if uncovered:
        print(f"  Uncovered modes: {', '.join(uncovered)}")
    print(sep)

    # Machine-readable JSON to stderr
    result = {
        "status": "ok",
        "org_name": token.get("org_name", ""),
        "patient_id": token.get("patient_id", ""),
        "expired": expired,
        "expires_at": token.get("expires_at", ""),
        "granted_scopes": sorted(granted),
        "scope_details": scope_details,
        "covered_modes": sorted(covered_modes),
        "uncovered_modes": uncovered,
    }
    sys.stderr.write(json.dumps(result) + "\n")


# --- Helpers ---

def _get_test_client(args) -> FHIRClient:
    """Get a FHIRClient for sandbox testing, using stored token."""
    org_id = getattr(args, "org_id", None)
    try:
        client = get_client(org_id)
    except FHIRError as e:
        print(json.dumps({
            "status": "error",
            "error": str(e),
            "hint": (
                "Run setup first, then authenticate:\n"
                "  python3 test_sandbox.py setup\n"
                "  python3 auth.py connect --sandbox\n"
                "  python3 test_sandbox.py test"
            ),
        }, indent=2))
        sys.exit(1)

    return client


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Epic FHIR sandbox test harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Workflow:\n"
            "  1. python3 test_sandbox.py setup          # register sandbox org\n"
            "  2. python3 auth.py connect --sandbox       # OAuth login with test patient\n"
            "  3. python3 test_sandbox.py scopes          # check granted scopes\n"
            "  4. python3 test_sandbox.py smoke           # quick 5-mode check\n"
            "  5. python3 test_sandbox.py test            # full 23-mode test\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    # setup
    p_setup = subparsers.add_parser(
        "setup",
        help="Register Epic sandbox as an org in the local DB",
    )
    p_setup.add_argument(
        "--client-id",
        default=None,
        help=f"Override sandbox client ID (default: {DEFAULT_SANDBOX_CLIENT_ID})",
    )

    # test
    p_test = subparsers.add_parser(
        "test",
        help="Run all 23 data modes against the sandbox",
    )
    p_test.add_argument("--org-id", type=int, default=None, help="Org ID (uses default if omitted)")

    # smoke
    p_smoke = subparsers.add_parser(
        "smoke",
        help="Quick 5-mode check (patient, labs, meds, conditions, vitals)",
    )
    p_smoke.add_argument("--org-id", type=int, default=None, help="Org ID (uses default if omitted)")

    # scopes
    p_scopes = subparsers.add_parser(
        "scopes",
        help="List granted FHIR scopes and map to available modes",
    )
    p_scopes.add_argument("--org-id", type=int, default=None, help="Org ID (uses default if omitted)")

    args = parser.parse_args()

    commands = {
        "setup":  cmd_setup,
        "test":   cmd_test,
        "smoke":  cmd_smoke,
        "scopes": cmd_scopes,
    }

    handler = commands.get(args.command)
    if not handler:
        parser.print_help()
        sys.exit(1)

    handler(args)


if __name__ == "__main__":
    main()
