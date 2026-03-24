#!/usr/bin/env python3
"""MyChart FHIR skill — main entry point and mode dispatcher.

Usage:
    python3 mychart.py labs [--org "name"] [--format json|compact|markdown] [--count N] [--since DATE]
    python3 mychart.py meds [options]
    python3 mychart.py conditions [options]
    python3 mychart.py allergies [options]
    python3 mychart.py vitals [options]
    python3 mychart.py summary [options]
    python3 mychart.py patient [options]
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add script dir to path for lib imports
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib import token_store
from lib.fhir_client import FHIRClient, FHIRError, get_client
from lib.display import format_resources


def _output(data, format_mode: str = "compact"):
    """Print output as JSON."""
    if isinstance(data, str):
        print(data)
    else:
        print(json.dumps(data, indent=2))


def _date_param(since: str = None, days: int = 365) -> str:
    """Build a FHIR date search parameter (ge prefix)."""
    if since:
        return f"ge{since}"
    cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    return f"ge{cutoff}"


def handle_labs(args):
    """Fetch lab results."""
    client = get_client()
    params = {
        "category": "laboratory",
        "_sort": "-date",
        "_count": str(args.count),
    }
    if args.since:
        params["date"] = _date_param(args.since)

    results = client.search("Observation", params)
    formatted = format_resources(results, "Observation:laboratory", args.format)
    print(formatted)


def handle_vitals(args):
    """Fetch vital signs."""
    client = get_client()
    params = {
        "category": "vital-signs",
        "_sort": "-date",
        "_count": str(args.count),
    }
    if args.since:
        params["date"] = _date_param(args.since)

    results = client.search("Observation", params)
    formatted = format_resources(results, "Observation:vital-signs", args.format)
    print(formatted)


def handle_meds(args):
    """Fetch medications."""
    client = get_client()
    params = {
        "_sort": "-authoredon",
        "_count": str(args.count),
    }
    if args.active_only:
        params["status"] = "active"

    results = client.search("MedicationRequest", params)
    formatted = format_resources(results, "MedicationRequest", args.format)
    print(formatted)


def handle_conditions(args):
    """Fetch conditions/diagnoses."""
    client = get_client()
    params = {"_count": str(args.count)}
    if args.active_only:
        params["clinical-status"] = "active"

    results = client.search("Condition", params)
    formatted = format_resources(results, "Condition", args.format)
    print(formatted)


def handle_allergies(args):
    """Fetch allergies and intolerances."""
    client = get_client()
    params = {"_count": str(args.count)}
    if args.active_only:
        params["clinical-status"] = "active"

    results = client.search("AllergyIntolerance", params)
    formatted = format_resources(results, "AllergyIntolerance", args.format)
    print(formatted)


def handle_patient(args):
    """Fetch patient demographics."""
    client = get_client()
    patient = client.get_patient()

    if args.format == "json":
        print(json.dumps(patient, indent=2))
        return

    # Extract key demographics
    name_parts = patient.get("name", [{}])[0]
    given = " ".join(name_parts.get("given", []))
    family = name_parts.get("family", "")

    addresses = patient.get("address", [])
    addr = ""
    if addresses:
        a = addresses[0]
        lines = ", ".join(a.get("line", []))
        addr = f"{lines}, {a.get('city', '')}, {a.get('state', '')} {a.get('postalCode', '')}"

    telecoms = patient.get("telecom", [])
    phone = ""
    email = ""
    for t in telecoms:
        if t.get("system") == "phone" and not phone:
            phone = t.get("value", "")
        if t.get("system") == "email" and not email:
            email = t.get("value", "")

    result = {
        "name": f"{given} {family}".strip(),
        "dob": patient.get("birthDate", ""),
        "gender": patient.get("gender", ""),
        "address": addr.strip(", "),
        "phone": phone,
        "email": email,
        "mrn": patient.get("id", ""),
    }
    print(json.dumps(result, indent=2))


def handle_summary(args):
    """Fetch a comprehensive health summary (multiple resource types)."""
    client = get_client()
    summary = {}
    errors = []

    # Fetch each resource type, collecting what we can
    fetches = [
        ("patient", "Patient", {"_id": client.patient_id} if client.patient_id else {}),
        ("conditions", "Condition", {"clinical-status": "active", "_count": "20"}),
        ("allergies", "AllergyIntolerance", {"clinical-status": "active", "_count": "20"}),
        ("medications", "MedicationRequest", {"status": "active", "_count": "20"}),
        ("recent_labs", "Observation", {"category": "laboratory", "_sort": "-date", "_count": "10"}),
        ("recent_vitals", "Observation", {"category": "vital-signs", "_sort": "-date", "_count": "10"}),
    ]

    for key, resource_type, params in fetches:
        try:
            results = client.search(resource_type, params)
            summary[key] = results
        except FHIRError as e:
            errors.append({"resource": key, "error": str(e)})
            summary[key] = []

    if args.format == "json":
        print(json.dumps({"summary": summary, "errors": errors}, indent=2))
        return

    # Compact format for Claude synthesis
    sections = []
    sections.append(f"## Health Summary ({datetime.utcnow().strftime('%Y-%m-%d')})")

    if summary.get("patient"):
        p = summary["patient"][0] if summary["patient"] else {}
        name_parts = p.get("name", [{}])[0] if p else {}
        given = " ".join(name_parts.get("given", []))
        family = name_parts.get("family", "")
        sections.append(f"\n### Patient: {given} {family}")
        sections.append(f"DOB: {p.get('birthDate', 'N/A')} | Gender: {p.get('gender', 'N/A')}")

    if summary.get("conditions"):
        sections.append(f"\n### Active Conditions ({len(summary['conditions'])})")
        formatted = format_resources(summary["conditions"], "Condition", "compact")
        sections.append(formatted)

    if summary.get("allergies"):
        sections.append(f"\n### Allergies ({len(summary['allergies'])})")
        formatted = format_resources(summary["allergies"], "AllergyIntolerance", "compact")
        sections.append(formatted)

    if summary.get("medications"):
        sections.append(f"\n### Active Medications ({len(summary['medications'])})")
        formatted = format_resources(summary["medications"], "MedicationRequest", "compact")
        sections.append(formatted)

    if summary.get("recent_labs"):
        sections.append(f"\n### Recent Labs ({len(summary['recent_labs'])})")
        formatted = format_resources(summary["recent_labs"], "Observation:laboratory", "compact")
        sections.append(formatted)

    if summary.get("recent_vitals"):
        sections.append(f"\n### Recent Vitals ({len(summary['recent_vitals'])})")
        formatted = format_resources(summary["recent_vitals"], "Observation:vital-signs", "compact")
        sections.append(formatted)

    if errors:
        sections.append(f"\n### Unavailable ({len(errors)} resources)")
        for e in errors:
            sections.append(f"  {e['resource']}: {e['error']}")

    print("\n".join(sections))


def main():
    parser = argparse.ArgumentParser(description="MyChart FHIR data access")
    parser.add_argument("--format", choices=["compact", "json", "markdown"], default="compact")
    parser.add_argument("--count", type=int, default=25, help="Max results per query")
    parser.add_argument("--since", help="Date filter (YYYY-MM-DD)")
    parser.add_argument("--active-only", action="store_true", help="Only show active items")

    subparsers = parser.add_subparsers(dest="mode")

    subparsers.add_parser("labs", help="Lab results")
    subparsers.add_parser("vitals", help="Vital signs")
    subparsers.add_parser("meds", help="Medications")
    subparsers.add_parser("conditions", help="Conditions/diagnoses")
    subparsers.add_parser("allergies", help="Allergies")
    subparsers.add_parser("patient", help="Patient demographics")
    subparsers.add_parser("summary", help="Comprehensive health summary")

    args = parser.parse_args()

    try:
        handlers = {
            "labs": handle_labs,
            "vitals": handle_vitals,
            "meds": handle_meds,
            "conditions": handle_conditions,
            "allergies": handle_allergies,
            "patient": handle_patient,
            "summary": handle_summary,
        }

        handler = handlers.get(args.mode)
        if not handler:
            parser.print_help()
            sys.exit(1)

        handler(args)

    except FHIRError as e:
        print(json.dumps({"status": "error", "error": str(e)}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "error": f"Unexpected error: {e}"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
