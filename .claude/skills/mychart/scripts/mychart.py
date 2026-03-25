#!/usr/bin/env python3
"""MyChart FHIR skill — main entry point and mode dispatcher.

Usage:
    python3 mychart.py labs [--org "name"] [--format json|compact|markdown] [--count N] [--since DATE]
    python3 mychart.py meds [options]
    python3 mychart.py conditions [options]
    python3 mychart.py allergies [options]
    python3 mychart.py vitals [options]
    python3 mychart.py immunizations [options]
    python3 mychart.py appointments [options]
    python3 mychart.py procedures [options]
    python3 mychart.py encounters [options]
    python3 mychart.py documents [options]
    python3 mychart.py coverage [options]
    python3 mychart.py careplans [options]
    python3 mychart.py goals [options]
    python3 mychart.py familyhistory [options]
    python3 mychart.py diagnostics [options]
    python3 mychart.py everything [options]
    python3 mychart.py lastn [--category vital-signs|laboratory] [--max N]
    python3 mychart.py search --type ResourceType [--params key=val ...]
    python3 mychart.py drug <name> [--type label|event|ndc]
    python3 mychart.py icd10 <query>
    python3 mychart.py interactions <drug1> <drug2> [drug3 ...]
    python3 mychart.py providers [--specialty X] [--condition X] [--zip-code X]
    python3 mychart.py trials <condition> [--location X] [--nct-id X]
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
    client = get_client(org_id=getattr(args, "org_id", None))
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
    client = get_client(org_id=getattr(args, "org_id", None))
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
    client = get_client(org_id=getattr(args, "org_id", None))
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
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_count": str(args.count)}
    if args.active_only:
        params["clinical-status"] = "active"

    results = client.search("Condition", params)
    formatted = format_resources(results, "Condition", args.format)
    print(formatted)


def handle_allergies(args):
    """Fetch allergies and intolerances."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_count": str(args.count)}
    if args.active_only:
        params["clinical-status"] = "active"

    results = client.search("AllergyIntolerance", params)
    formatted = format_resources(results, "AllergyIntolerance", args.format)
    print(formatted)


def handle_patient(args):
    """Fetch patient demographics."""
    client = get_client(org_id=getattr(args, "org_id", None))
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


def handle_immunizations(args):
    """Fetch immunization history."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_sort": "-date", "_count": str(args.count)}
    if args.since:
        params["date"] = _date_param(args.since)
    results = client.search("Immunization", params)
    print(format_resources(results, "Immunization", args.format))


def handle_appointments(args):
    """Fetch appointments."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_sort": "date", "_count": str(args.count)}
    if args.since:
        params["date"] = _date_param(args.since)
    elif not args.past:
        # Default: future appointments
        params["date"] = f"ge{datetime.utcnow().strftime('%Y-%m-%d')}"
    results = client.search("Appointment", params)
    print(format_resources(results, "Appointment", args.format))


def handle_procedures(args):
    """Fetch procedure history."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_sort": "-date", "_count": str(args.count)}
    if args.since:
        params["date"] = _date_param(args.since)
    results = client.search("Procedure", params)
    print(format_resources(results, "Procedure", args.format))


def handle_encounters(args):
    """Fetch encounter/visit history."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_sort": "-date", "_count": str(args.count)}
    if args.since:
        params["date"] = _date_param(args.since)
    results = client.search("Encounter", params)
    print(format_resources(results, "Encounter", args.format))


def handle_documents(args):
    """Fetch clinical documents."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_sort": "-date", "_count": str(args.count)}
    if args.doc_type:
        params["type"] = args.doc_type
    results = client.search("DocumentReference", params)
    print(format_resources(results, "DocumentReference", args.format))


def handle_coverage(args):
    """Fetch insurance/coverage information."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_count": str(args.count)}
    if args.active_only:
        params["status"] = "active"
    results = client.search("Coverage", params)
    print(format_resources(results, "Coverage", args.format))


def handle_careplans(args):
    """Fetch care plans."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_count": str(args.count)}
    if args.active_only:
        params["status"] = "active"
    results = client.search("CarePlan", params)
    print(format_resources(results, "CarePlan", args.format))


def handle_goals(args):
    """Fetch health goals."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_count": str(args.count)}
    if args.active_only:
        params["lifecycle-status"] = "active"
    results = client.search("Goal", params)
    print(format_resources(results, "Goal", args.format))


def handle_familyhistory(args):
    """Fetch family medical history."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_count": str(args.count)}
    results = client.search("FamilyMemberHistory", params)
    print(format_resources(results, "FamilyMemberHistory", args.format))


def handle_diagnostics(args):
    """Fetch diagnostic reports."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {"_sort": "-date", "_count": str(args.count)}
    if args.since:
        params["date"] = _date_param(args.since)
    results = client.search("DiagnosticReport", params)
    print(format_resources(results, "DiagnosticReport", args.format))


def handle_everything(args):
    """Fetch all patient data via $everything operation."""
    client = get_client(org_id=getattr(args, "org_id", None))
    try:
        results = client.everything()
        # Group by resource type
        grouped = {}
        for r in results:
            rt = r.get("resourceType", "Unknown")
            grouped.setdefault(rt, []).append(r)

        if args.format == "json":
            print(json.dumps(grouped, indent=2))
            return

        sections = [f"## Patient $everything ({len(results)} total resources)"]
        for rt, resources in sorted(grouped.items()):
            sections.append(f"\n### {rt} ({len(resources)})")
            formatted = format_resources(resources, rt, "compact")
            sections.append(formatted)
        print("\n".join(sections))

    except FHIRError as e:
        # Fall back to manual multi-fetch if $everything not supported
        print(f"$everything not supported by server: {e}", file=sys.stderr)
        print("Falling back to summary mode...", file=sys.stderr)
        handle_summary(args)


def handle_lastn(args):
    """Fetch latest observations per code via $lastn."""
    client = get_client(org_id=getattr(args, "org_id", None))
    category = getattr(args, "category", "vital-signs")
    max_per = getattr(args, "max", 1)
    try:
        results = client.lastn(category=category, max_per_code=max_per)
        obs_type = f"Observation:{category}"
        print(format_resources(results, obs_type, args.format))
    except FHIRError as e:
        print(f"$lastn not supported: {e}", file=sys.stderr)
        # Fall back to regular search
        params = {"category": category, "_sort": "-date", "_count": "20"}
        results = client.search("Observation", params)
        print(format_resources(results, f"Observation:{category}", args.format))


def handle_search(args):
    """Generic FHIR resource search."""
    client = get_client(org_id=getattr(args, "org_id", None))
    params = {}
    for p in (args.params or []):
        if "=" in p:
            k, v = p.split("=", 1)
            params[k] = v
    params["_count"] = str(args.count)
    results = client.search(args.type, params)
    print(format_resources(results, args.type, args.format))


def handle_drug(args):
    """Look up FDA drug information."""
    from lib.clinical import fda_drug_search
    result = fda_drug_search(args.drug_name, args.drug_type)
    print(json.dumps(result, indent=2))


def handle_icd10(args):
    """Look up ICD-10 codes."""
    from lib.clinical import icd10_lookup
    result = icd10_lookup(args.query, max_results=args.count)
    print(json.dumps(result, indent=2))


def handle_interactions(args):
    """Check drug-drug interactions."""
    from lib.clinical import check_drug_interactions
    result = check_drug_interactions(args.drugs)
    print(json.dumps(result, indent=2))


def handle_providers(args):
    """Search for healthcare providers via NPI Registry."""
    from lib.providers import search_providers, find_providers_for_conditions
    condition = getattr(args, "condition", None)
    if condition:
        zip_code = getattr(args, "zip_code", None) or ""
        result = find_providers_for_conditions(
            [c.strip() for c in condition.split(",")],
            zip_code=zip_code,
        )
    else:
        result = search_providers(
            specialty=getattr(args, "specialty", None),
            city=getattr(args, "city", None),
            state=getattr(args, "state", None),
            zip_code=getattr(args, "zip_code", None),
            name=getattr(args, "name", None),
            limit=args.count,
        )
    print(json.dumps(result, indent=2))


def handle_trials(args):
    """Search ClinicalTrials.gov for recruiting trials."""
    from lib.trials import search_trials, match_trials_to_conditions, get_trial_details
    nct_id = getattr(args, "nct_id", None)
    query = getattr(args, "query", None)
    location = getattr(args, "location", None)
    status = getattr(args, "status", "RECRUITING")
    if nct_id:
        result = get_trial_details(nct_id)
    elif query and "," in query:
        conditions = [c.strip() for c in query.split(",")]
        result = match_trials_to_conditions(conditions, location=location, status=status)
    else:
        if not query:
            print(json.dumps({"error": "Provide a condition to search for, or use --nct-id"}), file=sys.stderr)
            sys.exit(1)
        result = search_trials(query, status=status, location=location, max_results=args.count)
    print(json.dumps(result, indent=2))


def handle_summary(args):
    """Fetch a comprehensive health summary (multiple resource types)."""
    client = get_client(org_id=getattr(args, "org_id", None))
    summary = {}
    errors = []

    fetches = [
        ("patient", "Patient", {"_id": client.patient_id} if client.patient_id else {}),
        ("conditions", "Condition", {"clinical-status": "active", "_count": "20"}),
        ("allergies", "AllergyIntolerance", {"clinical-status": "active", "_count": "20"}),
        ("medications", "MedicationRequest", {"status": "active", "_count": "20"}),
        ("recent_labs", "Observation", {"category": "laboratory", "_sort": "-date", "_count": "10"}),
        ("recent_vitals", "Observation", {"category": "vital-signs", "_sort": "-date", "_count": "10"}),
        ("immunizations", "Immunization", {"_sort": "-date", "_count": "10"}),
        ("upcoming_appointments", "Appointment", {"date": f"ge{datetime.utcnow().strftime('%Y-%m-%d')}", "_sort": "date", "_count": "5"}),
        ("coverage", "Coverage", {"status": "active", "_count": "5"}),
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

    sections = []
    sections.append(f"## Health Summary ({datetime.utcnow().strftime('%Y-%m-%d')})")

    if summary.get("patient"):
        p = summary["patient"][0] if summary["patient"] else {}
        name_parts = p.get("name", [{}])[0] if p else {}
        given = " ".join(name_parts.get("given", []))
        family = name_parts.get("family", "")
        sections.append(f"\n### Patient: {given} {family}")
        sections.append(f"DOB: {p.get('birthDate', 'N/A')} | Gender: {p.get('gender', 'N/A')}")

    type_map = {
        "conditions": ("Active Conditions", "Condition"),
        "allergies": ("Allergies", "AllergyIntolerance"),
        "medications": ("Active Medications", "MedicationRequest"),
        "recent_labs": ("Recent Labs", "Observation:laboratory"),
        "recent_vitals": ("Recent Vitals", "Observation:vital-signs"),
        "immunizations": ("Immunizations", "Immunization"),
        "upcoming_appointments": ("Upcoming Appointments", "Appointment"),
        "coverage": ("Insurance/Coverage", "Coverage"),
    }

    for key, (label, rt) in type_map.items():
        data = summary.get(key, [])
        if data:
            sections.append(f"\n### {label} ({len(data)})")
            sections.append(format_resources(data, rt, "compact"))

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
    parser.add_argument("--past", action="store_true", help="Include past items (appointments)")
    parser.add_argument("--org", type=int, dest="org_id", help="Organization ID (uses default if omitted)")

    subparsers = parser.add_subparsers(dest="mode")

    subparsers.add_parser("labs", help="Lab results")
    subparsers.add_parser("vitals", help="Vital signs")
    subparsers.add_parser("meds", help="Medications")
    subparsers.add_parser("conditions", help="Conditions/diagnoses")
    subparsers.add_parser("allergies", help="Allergies")
    subparsers.add_parser("patient", help="Patient demographics")
    subparsers.add_parser("summary", help="Comprehensive health summary")
    subparsers.add_parser("immunizations", help="Immunization history")
    subparsers.add_parser("appointments", help="Appointments (future by default, --past for all)")

    docs_parser = subparsers.add_parser("documents", help="Clinical documents")
    docs_parser.add_argument("--doc-type", help="Filter by document type code")

    subparsers.add_parser("procedures", help="Procedure history")
    subparsers.add_parser("encounters", help="Visit/encounter history")
    subparsers.add_parser("coverage", help="Insurance/coverage info")
    subparsers.add_parser("careplans", help="Care plans")
    subparsers.add_parser("goals", help="Health goals")
    subparsers.add_parser("familyhistory", help="Family medical history")
    subparsers.add_parser("diagnostics", help="Diagnostic reports")
    subparsers.add_parser("everything", help="All patient data ($everything)")

    lastn_parser = subparsers.add_parser("lastn", help="Latest observations per code ($lastn)")
    lastn_parser.add_argument("--category", default="vital-signs", help="Observation category")
    lastn_parser.add_argument("--max", type=int, default=1, help="Max per code")

    search_parser = subparsers.add_parser("search", help="Generic FHIR resource search")
    search_parser.add_argument("--type", required=True, help="FHIR resource type")
    search_parser.add_argument("--params", nargs="*", help="Search params as key=value")

    # Clinical knowledge tools (no auth required)
    drug_parser = subparsers.add_parser("drug", help="FDA drug lookup")
    drug_parser.add_argument("drug_name", help="Drug name (brand or generic)")
    drug_parser.add_argument("--drug-type", choices=["label", "event", "ndc"], default="label", help="Search type")

    icd10_parser = subparsers.add_parser("icd10", help="ICD-10 code lookup")
    icd10_parser.add_argument("query", help="ICD-10 code or condition name")

    interactions_parser = subparsers.add_parser("interactions", help="Drug interaction checker")
    interactions_parser.add_argument("drugs", nargs="+", help="Two or more drug names")

    # Provider finder (no auth required)
    providers_parser = subparsers.add_parser("providers", help="Search for healthcare providers (NPI Registry)")
    providers_parser.add_argument("--specialty", help="Medical specialty (e.g., 'Cardiology')")
    providers_parser.add_argument("--condition", help="Condition name(s), comma-separated (auto-maps to specialty)")
    providers_parser.add_argument("--zip-code", help="ZIP code to search near")
    providers_parser.add_argument("--city", help="City name")
    providers_parser.add_argument("--state", help="Two-letter state code")
    providers_parser.add_argument("--name", help="Provider name")

    # Clinical trials (no auth required)
    trials_parser = subparsers.add_parser("trials", help="Search ClinicalTrials.gov for recruiting trials")
    trials_parser.add_argument("query", nargs="?", help="Condition to search for")
    trials_parser.add_argument("--nct-id", help="Get details for a specific trial by NCT ID")
    trials_parser.add_argument("--location", help="Location filter (city, state, or country)")
    trials_parser.add_argument("--status", default="RECRUITING", help="Trial status (default: RECRUITING)")

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
            "immunizations": handle_immunizations,
            "appointments": handle_appointments,
            "procedures": handle_procedures,
            "encounters": handle_encounters,
            "documents": handle_documents,
            "coverage": handle_coverage,
            "careplans": handle_careplans,
            "goals": handle_goals,
            "familyhistory": handle_familyhistory,
            "diagnostics": handle_diagnostics,
            "everything": handle_everything,
            "lastn": handle_lastn,
            "search": handle_search,
            "drug": handle_drug,
            "icd10": handle_icd10,
            "interactions": handle_interactions,
            "providers": handle_providers,
            "trials": handle_trials,
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
