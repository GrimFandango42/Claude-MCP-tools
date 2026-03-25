"""CMS hospital quality data — Compare hospitals, nursing homes, and home health agencies.

Uses the CMS data.cms.gov SODA API (public, no key required).
"""

import json
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlencode

from . import http


# CMS SODA API endpoints (public, no auth needed)
# Hospital General Information
HOSPITAL_INFO = "https://data.cms.gov/provider-data/api/1/datastore/query/xubh-q36u/0"
# Hospital Quality Star Ratings (Overall)
HOSPITAL_STARS = "https://data.cms.gov/provider-data/api/1/datastore/query/bn3u-3s97/0"
# Patient Survey (HCAHPS)
HOSPITAL_SURVEY = "https://data.cms.gov/provider-data/api/1/datastore/query/dgck-syfz/0"
# Timely and Effective Care
HOSPITAL_CARE = "https://data.cms.gov/provider-data/api/1/datastore/query/yv7e-xc69/0"
# Complications and Deaths
HOSPITAL_OUTCOMES = "https://data.cms.gov/provider-data/api/1/datastore/query/ynj2-r877/0"


def search_hospitals(
    name: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """Search CMS Hospital Compare for hospital info + quality ratings.

    Args:
        name: Hospital name (partial match)
        city: City name
        state: Two-letter state code
        zip_code: ZIP code
        limit: Max results (1-25)

    Returns:
        Dict with hospital info, star ratings, and ownership details
    """
    conditions = []
    if name:
        conditions.append({"resource": "t", "property": "hospital_name", "value": f"%{name}%", "operator": "LIKE"})
    if city:
        conditions.append({"resource": "t", "property": "city", "value": city.upper(), "operator": "="})
    if state:
        conditions.append({"resource": "t", "property": "state", "value": state.upper(), "operator": "="})
    if zip_code:
        conditions.append({"resource": "t", "property": "zip_code", "value": zip_code, "operator": "="})

    if not conditions:
        return {"error": "Provide at least one search parameter (name, city, state, or zip_code)"}

    limit = min(max(limit, 1), 25)

    payload = {
        "conditions": conditions,
        "limit": limit,
        "offset": 0,
        "sorts": [{"property": "hospital_name", "order": "asc"}],
    }

    try:
        data = http.request("POST", HOSPITAL_INFO, json_data=payload, retries=2)
        results = data.get("results", [])

        hospitals = []
        for r in results:
            hospitals.append({
                "provider_id": r.get("facility_id", ""),
                "name": r.get("hospital_name", ""),
                "address": r.get("address", ""),
                "city": r.get("city", ""),
                "state": r.get("state", ""),
                "zip_code": r.get("zip_code", ""),
                "phone": r.get("telephone_number", ""),
                "type": r.get("hospital_type", ""),
                "ownership": r.get("hospital_ownership", ""),
                "overall_rating": r.get("hospital_overall_rating", "N/A"),
                "emergency_services": r.get("emergency_services", ""),
                "meets_ehr_criteria": r.get("meets_criteria_for_promoting_interoperability_of_ehrs", ""),
            })

        return {
            "query": {k: v for k, v in {"name": name, "city": city, "state": state, "zip_code": zip_code}.items() if v},
            "count": len(hospitals),
            "hospitals": hospitals,
        }

    except http.HTTPError as e:
        return {"error": f"CMS API error: {e}"}


def hospital_ratings(provider_id: str) -> Dict[str, Any]:
    """Get detailed quality ratings for a specific hospital.

    Args:
        provider_id: CMS facility/provider ID (6-digit)

    Returns:
        Dict with star ratings across quality domains
    """
    payload = {
        "conditions": [
            {"resource": "t", "property": "facility_id", "value": provider_id, "operator": "="}
        ],
        "limit": 1,
    }

    try:
        data = http.request("POST", HOSPITAL_STARS, json_data=payload, retries=2)
        results = data.get("results", [])

        if not results:
            return {"provider_id": provider_id, "error": "No ratings found for this facility"}

        r = results[0]
        return {
            "provider_id": provider_id,
            "hospital_name": r.get("facility_name", ""),
            "overall_rating": r.get("hospital_overall_rating", "N/A"),
            "mortality_rating": r.get("mortality_national_comparison", "N/A"),
            "safety_rating": r.get("safety_of_care_national_comparison", "N/A"),
            "readmission_rating": r.get("readmission_national_comparison", "N/A"),
            "patient_experience_rating": r.get("patient_experience_national_comparison", "N/A"),
            "effectiveness_rating": r.get("effectiveness_of_care_national_comparison", "N/A"),
            "timeliness_rating": r.get("timeliness_of_care_national_comparison", "N/A"),
            "efficient_imaging_rating": r.get("efficient_use_of_medical_imaging_national_comparison", "N/A"),
        }

    except http.HTTPError as e:
        return {"provider_id": provider_id, "error": f"CMS API error: {e}"}


def hospital_patient_experience(provider_id: str) -> Dict[str, Any]:
    """Get HCAHPS patient satisfaction survey results for a hospital.

    Args:
        provider_id: CMS facility/provider ID

    Returns:
        Dict with patient survey scores across dimensions
    """
    payload = {
        "conditions": [
            {"resource": "t", "property": "facility_id", "value": provider_id, "operator": "="}
        ],
        "limit": 25,
    }

    try:
        data = http.request("POST", HOSPITAL_SURVEY, json_data=payload, retries=2)
        results = data.get("results", [])

        if not results:
            return {"provider_id": provider_id, "error": "No survey data found"}

        hospital_name = results[0].get("facility_name", "")
        measures = []
        for r in results:
            measures.append({
                "measure": r.get("hcahps_measure_id", ""),
                "question": r.get("hcahps_question", ""),
                "answer_description": r.get("hcahps_answer_description", ""),
                "hospital_score": r.get("patient_survey_star_rating", "N/A"),
                "star_rating": r.get("patient_survey_star_rating", "N/A"),
                "response_rate": r.get("survey_response_rate_percent", "N/A"),
            })

        return {
            "provider_id": provider_id,
            "hospital_name": hospital_name,
            "measures": measures,
        }

    except http.HTTPError as e:
        return {"provider_id": provider_id, "error": f"CMS API error: {e}"}
