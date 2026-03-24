"""Provider finder — NPI Registry search for healthcare providers.

Uses the free, public CMS NPI Registry API (no key required).
"""

from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from . import http


NPI_BASE = "https://npiregistry.cms.hhs.gov/api/?version=2.1"

# Maps common conditions/diagnoses to relevant medical specialties.
CONDITION_SPECIALTY_MAP: Dict[str, str] = {
    "diabetes": "Endocrinology",
    "thyroid": "Endocrinology",
    "hormone": "Endocrinology",
    "pcos": "Endocrinology",
    "osteoporosis": "Endocrinology",
    "hypertension": "Cardiology",
    "heart disease": "Cardiology",
    "heart failure": "Cardiology",
    "arrhythmia": "Cardiology",
    "atrial fibrillation": "Cardiology",
    "cholesterol": "Cardiology",
    "asthma": "Pulmonology",
    "copd": "Pulmonology",
    "pneumonia": "Pulmonology",
    "sleep apnea": "Pulmonology",
    "arthritis": "Rheumatology",
    "lupus": "Rheumatology",
    "fibromyalgia": "Rheumatology",
    "gout": "Rheumatology",
    "back pain": "Orthopedic Surgery",
    "fracture": "Orthopedic Surgery",
    "joint pain": "Orthopedic Surgery",
    "depression": "Psychiatry & Neurology",
    "anxiety": "Psychiatry & Neurology",
    "bipolar": "Psychiatry & Neurology",
    "adhd": "Psychiatry & Neurology",
    "schizophrenia": "Psychiatry & Neurology",
    "migraine": "Neurology",
    "epilepsy": "Neurology",
    "seizure": "Neurology",
    "multiple sclerosis": "Neurology",
    "parkinson": "Neurology",
    "cancer": "Hematology & Oncology",
    "tumor": "Hematology & Oncology",
    "leukemia": "Hematology & Oncology",
    "lymphoma": "Hematology & Oncology",
    "kidney disease": "Nephrology",
    "kidney stones": "Urology",
    "uti": "Urology",
    "prostate": "Urology",
    "ibs": "Gastroenterology",
    "crohn": "Gastroenterology",
    "colitis": "Gastroenterology",
    "acid reflux": "Gastroenterology",
    "gerd": "Gastroenterology",
    "liver disease": "Gastroenterology",
    "hepatitis": "Gastroenterology",
    "eczema": "Dermatology",
    "psoriasis": "Dermatology",
    "acne": "Dermatology",
    "skin cancer": "Dermatology",
    "allergy": "Allergy & Immunology",
    "sinusitis": "Otolaryngology",
    "hearing loss": "Otolaryngology",
    "pregnancy": "Obstetrics & Gynecology",
    "fertility": "Obstetrics & Gynecology",
    "endometriosis": "Obstetrics & Gynecology",
    "cataracts": "Ophthalmology",
    "glaucoma": "Ophthalmology",
    "macular degeneration": "Ophthalmology",
}


def _build_npi_url(params: Dict[str, str]) -> str:
    """Build NPI registry query URL from parameters."""
    clean = {k: v for k, v in params.items() if v}
    if clean:
        return f"{NPI_BASE}&{urlencode(clean)}"
    return NPI_BASE


def _format_provider(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format a single NPI result into a clean provider dict."""
    basic = result.get("basic", {})
    addresses = result.get("addresses", [])
    taxonomies = result.get("taxonomies", [])

    # Determine name based on entity type (1=individual, 2=organization)
    enum_type = result.get("enumeration_type", "")
    if enum_type == "NPI-1":
        first = basic.get("first_name", "")
        last = basic.get("last_name", "")
        credential = basic.get("credential", "")
        name = f"{first} {last}".strip()
        if credential:
            name = f"{name}, {credential}"
    else:
        name = basic.get("organization_name", basic.get("name", "Unknown"))

    # Primary practice address (prefer LOCATION over mailing)
    address = {}
    for addr in addresses:
        if addr.get("address_purpose", "") == "LOCATION":
            address = addr
            break
    if not address and addresses:
        address = addresses[0]

    formatted_address = ""
    if address:
        parts = [
            address.get("address_1", ""),
            address.get("address_2", ""),
        ]
        line = ", ".join(p for p in parts if p)
        city_state = (
            f"{address.get('city', '')}, "
            f"{address.get('state', '')} "
            f"{address.get('postal_code', '')[:5]}"
        )
        formatted_address = f"{line}, {city_state}" if line else city_state

    phone = address.get("telephone_number", "")

    # Specialties from taxonomies
    specialties = []
    primary_specialty = ""
    for tax in taxonomies:
        desc = tax.get("desc", "")
        if desc:
            specialties.append(desc)
        if tax.get("primary", False) and desc:
            primary_specialty = desc

    provider: Dict[str, Any] = {
        "npi": result.get("number", ""),
        "name": name,
        "entity_type": "Individual" if enum_type == "NPI-1" else "Organization",
        "primary_specialty": primary_specialty or (specialties[0] if specialties else ""),
        "all_specialties": specialties,
        "address": formatted_address,
        "phone": phone,
        "gender": basic.get("gender", ""),
    }

    status = basic.get("status", "")
    if status:
        provider["status"] = status

    return provider


def _query_npi(params: Dict[str, str], limit: int = 10) -> Dict[str, Any]:
    """Execute NPI registry query and return formatted results."""
    params["limit"] = str(min(limit, 200))  # API max is 200
    url = _build_npi_url(params)

    try:
        data = http.get(url, retries=2)
    except http.HTTPError as e:
        return {"error": f"NPI Registry request failed: {e}", "providers": []}

    result_count = data.get("result_count", 0)
    results = data.get("results", [])

    providers = [_format_provider(r) for r in results]

    return {
        "result_count": result_count,
        "providers": providers,
    }


def search_providers(
    specialty: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    name: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """Search the NPI Registry for healthcare providers.

    Args:
        specialty: Medical specialty / taxonomy description (e.g. "Cardiology")
        city: City name
        state: Two-letter state code (e.g. "CA")
        zip_code: ZIP / postal code
        name: Provider name — parsed as "first last" for individuals
        limit: Maximum results to return (max 200)

    Returns:
        Dict with result_count, providers list, and search criteria used
    """
    params: Dict[str, str] = {}

    if specialty:
        params["taxonomy_description"] = specialty
    if city:
        params["city"] = city
    if state:
        params["state"] = state
    if zip_code:
        params["postal_code"] = zip_code

    if name:
        parts = name.strip().split(None, 1)
        if len(parts) == 2:
            params["first_name"] = parts[0]
            params["last_name"] = parts[1]
        else:
            # Single token — try as last name (more common search pattern)
            params["last_name"] = parts[0]

    if not params:
        return {"error": "At least one search parameter is required", "providers": []}

    result = _query_npi(params, limit=limit)
    result["search_criteria"] = {
        k: v for k, v in {
            "specialty": specialty,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "name": name,
        }.items() if v
    }

    return result


def find_providers_for_conditions(
    conditions: List[str],
    zip_code: str,
    radius_miles: int = 25,
) -> Dict[str, Any]:
    """Find providers relevant to a list of medical conditions.

    Maps conditions to medical specialties using CONDITION_SPECIALTY_MAP, then
    searches the NPI Registry for those specialties near the given ZIP code.

    Args:
        conditions: List of condition names (e.g. ["diabetes", "hypertension"])
        zip_code: ZIP code to search near
        radius_miles: Search radius (noted in output; NPI API uses exact ZIP match)

    Returns:
        Dict with results grouped by specialty, plus unmapped conditions
    """
    specialty_conditions: Dict[str, List[str]] = {}
    unmapped: List[str] = []

    for condition in conditions:
        condition_lower = condition.lower().strip()
        matched = False
        for key, specialty in CONDITION_SPECIALTY_MAP.items():
            if key in condition_lower:
                specialty_conditions.setdefault(specialty, []).append(condition)
                matched = True
                break
        if not matched:
            unmapped.append(condition)

    if not specialty_conditions and unmapped:
        return {
            "zip_code": zip_code,
            "radius_miles": radius_miles,
            "note": "Could not map any conditions to specialties. Try searching by specialty name directly.",
            "unmapped_conditions": unmapped,
            "results_by_specialty": {},
        }

    # Search NPI for each mapped specialty
    results_by_specialty: Dict[str, Any] = {}

    for specialty, matched_conditions in specialty_conditions.items():
        result = _query_npi(
            {"taxonomy_description": specialty, "postal_code": zip_code},
            limit=10,
        )
        results_by_specialty[specialty] = {
            "matched_conditions": matched_conditions,
            "result_count": result.get("result_count", 0),
            "providers": result.get("providers", []),
        }

    output: Dict[str, Any] = {
        "zip_code": zip_code,
        "radius_miles": radius_miles,
        "note": (
            "NPI Registry searches by exact ZIP code. Providers in adjacent ZIPs "
            "may not appear. Broaden by searching with city/state if needed."
        ),
        "specialties_searched": list(specialty_conditions.keys()),
        "results_by_specialty": results_by_specialty,
    }

    if unmapped:
        output["unmapped_conditions"] = unmapped

    return output


def find_by_insurance(
    insurance_name: str,
    zip_code: str,
    specialty: Optional[str] = None,
) -> Dict[str, Any]:
    """Search for providers and note insurance for verification.

    The NPI Registry does not contain insurance network data. This function
    returns providers matching the location/specialty criteria along with a
    note that insurance network participation must be verified separately.

    Args:
        insurance_name: Name of insurance plan/company (for reference)
        zip_code: ZIP code to search near
        specialty: Optional specialty filter

    Returns:
        Dict with provider results and insurance verification note
    """
    params: Dict[str, str] = {"postal_code": zip_code}
    if specialty:
        params["taxonomy_description"] = specialty

    result = _query_npi(params, limit=10)

    return {
        "insurance": insurance_name,
        "zip_code": zip_code,
        "specialty": specialty,
        "insurance_note": (
            f"The NPI Registry does not include insurance network data. "
            f"The providers listed below are near ZIP {zip_code}"
            f"{' in ' + specialty if specialty else ''}, but their participation "
            f"in {insurance_name} networks has NOT been verified. "
            f"Please contact {insurance_name} directly or check their online "
            f"provider directory to confirm network coverage before scheduling."
        ),
        "result_count": result.get("result_count", 0),
        "providers": result.get("providers", []),
    }
