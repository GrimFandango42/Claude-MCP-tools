"""Clinical trials matching — ClinicalTrials.gov v2 API.

Searches recruiting trials by condition, matches patient conditions to trials,
and retrieves detailed trial information. No API key required.
"""

from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlencode

from . import http

CT_BASE = "https://clinicaltrials.gov/api/v2/studies"

MAX_ELIGIBILITY_LEN = 500
MAX_INTERVENTION_DESC_LEN = 200


def _truncate(text: Optional[str], max_len: int) -> str:
    """Truncate text to max_len, adding ellipsis if truncated."""
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def _extract_interventions(arms_module: Dict) -> List[str]:
    """Extract intervention names and types from armsInterventionsModule."""
    interventions = []
    for iv in arms_module.get("interventions", []):
        iv_type = iv.get("type", "")
        iv_name = iv.get("name", "")
        desc = _truncate(iv.get("description", ""), MAX_INTERVENTION_DESC_LEN)
        entry = f"{iv_type}: {iv_name}" if iv_type else iv_name
        if desc:
            entry += f" ({desc})"
        interventions.append(entry)
    return interventions


def _extract_locations(contacts_module: Dict, max_locations: int = 3) -> List[Dict[str, str]]:
    """Extract location info (facility, city, state, country)."""
    locations = []
    for loc in contacts_module.get("locations", [])[:max_locations]:
        locations.append({
            "facility": loc.get("facility", ""),
            "city": loc.get("city", ""),
            "state": loc.get("state", ""),
            "country": loc.get("country", ""),
        })
    return locations


def _extract_contacts(contacts_module: Dict) -> List[Dict[str, str]]:
    """Extract central contact information."""
    contacts = []
    for c in contacts_module.get("centralContacts", []):
        contacts.append({
            "name": c.get("name", ""),
            "role": c.get("role", ""),
            "phone": c.get("phone", ""),
            "email": c.get("email", ""),
        })
    return contacts


def _format_study(study: Dict) -> Dict[str, Any]:
    """Format a single study from the v2 API response into a clean dict."""
    proto = study.get("protocolSection", {})

    ident = proto.get("identificationModule", {})
    status_mod = proto.get("statusModule", {})
    design = proto.get("designModule", {})
    conditions_mod = proto.get("conditionsModule", {})
    arms_mod = proto.get("armsInterventionsModule", {})
    contacts_mod = proto.get("contactsLocationsModule", {})
    eligibility_mod = proto.get("eligibilityModule", {})
    sponsor_mod = proto.get("sponsorCollaboratorsModule", {})

    # Phase info
    phases = design.get("phases", [])
    phase_str = ", ".join(phases) if phases else "N/A"

    # Sponsor
    lead_sponsor = sponsor_mod.get("leadSponsor", {})
    sponsor_name = lead_sponsor.get("name", "N/A")

    # Dates
    start_info = status_mod.get("startDateStruct", {})
    completion_info = status_mod.get("completionDateStruct", {})
    start_date = start_info.get("date", "N/A")
    end_date = completion_info.get("date", "N/A")

    # Eligibility summary
    elig_criteria = _truncate(eligibility_mod.get("eligibilityCriteria", ""), MAX_ELIGIBILITY_LEN)

    return {
        "nctId": ident.get("nctId", ""),
        "title": ident.get("briefTitle", ""),
        "officialTitle": _truncate(ident.get("officialTitle", ""), 300),
        "status": status_mod.get("overallStatus", ""),
        "phase": phase_str,
        "conditions": conditions_mod.get("conditions", []),
        "interventions": _extract_interventions(arms_mod),
        "locations": _extract_locations(contacts_mod),
        "contacts": _extract_contacts(contacts_mod),
        "eligibilitySummary": elig_criteria,
        "sex": eligibility_mod.get("sex", ""),
        "minAge": eligibility_mod.get("minimumAge", ""),
        "maxAge": eligibility_mod.get("maximumAge", ""),
        "sponsor": sponsor_name,
        "startDate": start_date,
        "completionDate": end_date,
    }


def search_trials(
    condition: str,
    status: str = "RECRUITING",
    location: Optional[str] = None,
    max_results: int = 10,
) -> Dict[str, Any]:
    """Search ClinicalTrials.gov for trials matching a condition.

    Args:
        condition: Medical condition to search for (e.g., 'Type 2 Diabetes')
        status: Trial status filter (default: RECRUITING). Options include
                RECRUITING, NOT_YET_RECRUITING, ACTIVE_NOT_RECRUITING,
                COMPLETED, ENROLLING_BY_INVITATION, etc.
        location: Optional location filter (city, state, or country)
        max_results: Maximum number of results (1-50)

    Returns:
        Dict with totalCount and list of formatted trial summaries.
    """
    max_results = min(max(1, max_results), 50)

    params = {
        "query.cond": condition,
        "filter.overallStatus": status,
        "countTotal": "true",
        "pageSize": str(max_results),
    }
    if location:
        params["query.locn"] = location

    url = f"{CT_BASE}?{urlencode(params)}"

    try:
        data = http.get(url, retries=2)
        studies = data.get("studies", [])
        total = data.get("totalCount", len(studies))

        formatted = [_format_study(s) for s in studies]

        return {
            "condition": condition,
            "status": status,
            "location": location,
            "totalCount": total,
            "returnedCount": len(formatted),
            "trials": formatted,
        }

    except http.HTTPError as e:
        return {
            "condition": condition,
            "error": f"ClinicalTrials.gov API error: {e}",
            "status_code": getattr(e, "status_code", None),
        }


def match_trials_to_conditions(
    conditions: List[str],
    location: Optional[str] = None,
    status: str = "RECRUITING",
) -> Dict[str, Any]:
    """Search trials for multiple patient conditions and deduplicate.

    Takes a list of condition names (as from FHIR Condition resources),
    searches for recruiting trials for each, deduplicates by nctId, and
    groups results by condition.

    Args:
        conditions: List of condition names (e.g., from patient's problem list)
        location: Optional location filter
        status: Trial status filter

    Returns:
        Dict with per-condition results, deduplicated trial list, and totals.
    """
    seen_ncts: set = set()
    by_condition: Dict[str, List[Dict]] = {}
    all_unique: List[Dict] = []
    errors: List[str] = []

    for cond in conditions:
        result = search_trials(cond, status=status, location=location, max_results=10)

        if "error" in result:
            errors.append(f"{cond}: {result['error']}")
            by_condition[cond] = []
            continue

        cond_trials = []
        for trial in result.get("trials", []):
            nct = trial.get("nctId", "")
            cond_trials.append(trial)
            if nct and nct not in seen_ncts:
                seen_ncts.add(nct)
                all_unique.append(trial)

        by_condition[cond] = cond_trials

    return {
        "conditionsSearched": conditions,
        "location": location,
        "status": status,
        "byCondition": {
            cond: {
                "matchCount": len(trials),
                "trials": trials,
            }
            for cond, trials in by_condition.items()
        },
        "uniqueTrialCount": len(all_unique),
        "allUniqueTrials": all_unique,
        "errors": errors if errors else None,
    }


def get_trial_details(nct_id: str) -> Dict[str, Any]:
    """Retrieve comprehensive details for a single trial by NCT ID.

    Args:
        nct_id: ClinicalTrials.gov identifier (e.g., 'NCT12345678')

    Returns:
        Dict with full trial information including all locations,
        eligibility criteria, arms/interventions, and more.
    """
    url = f"{CT_BASE}/{quote(nct_id)}"

    try:
        study = http.get(url, retries=2)
    except http.HTTPError as e:
        if e.status_code == 404:
            return {"nctId": nct_id, "error": f"Trial {nct_id} not found"}
        return {"nctId": nct_id, "error": f"API error: {e}"}

    proto = study.get("protocolSection", {})

    ident = proto.get("identificationModule", {})
    status_mod = proto.get("statusModule", {})
    desc_mod = proto.get("descriptionModule", {})
    design = proto.get("designModule", {})
    conditions_mod = proto.get("conditionsModule", {})
    arms_mod = proto.get("armsInterventionsModule", {})
    contacts_mod = proto.get("contactsLocationsModule", {})
    eligibility_mod = proto.get("eligibilityModule", {})
    sponsor_mod = proto.get("sponsorCollaboratorsModule", {})
    outcomes_mod = proto.get("outcomesModule", {})

    # All locations (not truncated)
    all_locations = []
    for loc in contacts_mod.get("locations", []):
        all_locations.append({
            "facility": loc.get("facility", ""),
            "city": loc.get("city", ""),
            "state": loc.get("state", ""),
            "country": loc.get("country", ""),
            "zip": loc.get("zip", ""),
            "status": loc.get("status", ""),
        })

    # All arms
    arms = []
    for arm in arms_mod.get("arms", []):
        arms.append({
            "label": arm.get("label", ""),
            "type": arm.get("type", ""),
            "description": arm.get("description", ""),
            "interventionNames": arm.get("interventionNames", []),
        })

    # Interventions (full)
    interventions = []
    for iv in arms_mod.get("interventions", []):
        interventions.append({
            "type": iv.get("type", ""),
            "name": iv.get("name", ""),
            "description": iv.get("description", ""),
            "armGroupLabels": iv.get("armGroupLabels", []),
        })

    # Primary outcomes
    primary_outcomes = []
    for po in outcomes_mod.get("primaryOutcomes", []):
        primary_outcomes.append({
            "measure": po.get("measure", ""),
            "description": _truncate(po.get("description", ""), 300),
            "timeFrame": po.get("timeFrame", ""),
        })

    # Collaborators
    collaborators = [
        {"name": c.get("name", ""), "class": c.get("class", "")}
        for c in sponsor_mod.get("collaborators", [])
    ]

    lead_sponsor = sponsor_mod.get("leadSponsor", {})
    start_info = status_mod.get("startDateStruct", {})
    completion_info = status_mod.get("completionDateStruct", {})

    return {
        "nctId": ident.get("nctId", nct_id),
        "briefTitle": ident.get("briefTitle", ""),
        "officialTitle": ident.get("officialTitle", ""),
        "status": status_mod.get("overallStatus", ""),
        "phase": ", ".join(design.get("phases", [])) or "N/A",
        "studyType": design.get("studyType", ""),
        "briefSummary": _truncate(desc_mod.get("briefSummary", ""), 1000),
        "detailedDescription": _truncate(desc_mod.get("detailedDescription", ""), 2000),
        "conditions": conditions_mod.get("conditions", []),
        "keywords": conditions_mod.get("keywords", []),
        "arms": arms,
        "interventions": interventions,
        "eligibility": {
            "criteria": eligibility_mod.get("eligibilityCriteria", ""),
            "sex": eligibility_mod.get("sex", ""),
            "minAge": eligibility_mod.get("minimumAge", ""),
            "maxAge": eligibility_mod.get("maximumAge", ""),
            "healthyVolunteers": eligibility_mod.get("healthyVolunteers", ""),
            "stdAges": eligibility_mod.get("stdAges", []),
        },
        "locations": all_locations,
        "locationCount": len(all_locations),
        "contacts": _extract_contacts(contacts_mod),
        "sponsor": {
            "name": lead_sponsor.get("name", ""),
            "class": lead_sponsor.get("class", ""),
        },
        "collaborators": collaborators,
        "primaryOutcomes": primary_outcomes,
        "startDate": start_info.get("date", "N/A"),
        "completionDate": completion_info.get("date", "N/A"),
        "enrollmentInfo": proto.get("designModule", {}).get("enrollmentInfo", {}),
    }
