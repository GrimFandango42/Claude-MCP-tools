"""Clinical knowledge tools — FDA drug info, ICD-10 lookup, drug interactions, drug pricing.

Uses public FDA, NLM, and Cost Plus Drugs APIs (no keys required).
"""

import json
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlencode

from . import http


# --- FDA Drug Lookup (openFDA API) ---

FDA_BASE = "https://api.fda.gov/drug"


def fda_drug_search(drug_name: str, search_type: str = "label") -> Dict[str, Any]:
    """Search FDA drug database.

    Args:
        drug_name: Drug name (brand or generic)
        search_type: 'label' (drug info), 'event' (adverse events), 'ndc' (product codes)

    Returns:
        Formatted drug information dict
    """
    endpoints = {
        "label": f'{FDA_BASE}/label.json?search=openfda.brand_name:"{quote(drug_name)}"+openfda.generic_name:"{quote(drug_name)}"&limit=3',
        "event": f'{FDA_BASE}/event.json?search=patient.drug.openfda.brand_name:"{quote(drug_name)}"+patient.drug.openfda.generic_name:"{quote(drug_name)}"&count=patient.reaction.reactionmeddrapt.exact&limit=10',
        "ndc": f'{FDA_BASE}/ndc.json?search=brand_name:"{quote(drug_name)}"+generic_name:"{quote(drug_name)}"&limit=5',
    }

    url = endpoints.get(search_type, endpoints["label"])

    try:
        data = http.get(url, retries=2)
        results = data.get("results", [])

        if search_type == "label":
            return _format_drug_label(results, drug_name)
        elif search_type == "event":
            return _format_adverse_events(results, drug_name)
        elif search_type == "ndc":
            return _format_ndc(results, drug_name)
        return {"drug": drug_name, "results": results}

    except http.HTTPError as e:
        if e.status_code == 404:
            return {"drug": drug_name, "error": f"No FDA data found for '{drug_name}'"}
        raise


def _format_drug_label(results: List[Dict], drug_name: str) -> Dict[str, Any]:
    """Format FDA drug label results."""
    if not results:
        return {"drug": drug_name, "error": "No label data found"}

    label = results[0]
    openfda = label.get("openfda", {})

    return {
        "drug": drug_name,
        "brand_names": openfda.get("brand_name", []),
        "generic_names": openfda.get("generic_name", []),
        "manufacturer": openfda.get("manufacturer_name", []),
        "route": openfda.get("route", []),
        "substance": openfda.get("substance_name", []),
        "pharm_class": openfda.get("pharm_class_epc", []),
        "indications": _truncate_list(label.get("indications_and_usage", []), 500),
        "warnings": _truncate_list(label.get("warnings", []), 500),
        "contraindications": _truncate_list(label.get("contraindications", []), 300),
        "adverse_reactions": _truncate_list(label.get("adverse_reactions", []), 500),
        "drug_interactions": _truncate_list(label.get("drug_interactions", []), 500),
        "dosage": _truncate_list(label.get("dosage_and_administration", []), 500),
        "pregnancy": _truncate_list(label.get("pregnancy", []), 200),
    }


def _format_adverse_events(results: List[Dict], drug_name: str) -> Dict[str, Any]:
    """Format FDA adverse event counts."""
    if not results:
        return {"drug": drug_name, "adverse_events": []}

    events = [{"reaction": r["term"], "count": r["count"]} for r in results]
    return {"drug": drug_name, "top_adverse_events": events}


def _format_ndc(results: List[Dict], drug_name: str) -> Dict[str, Any]:
    """Format NDC product results."""
    if not results:
        return {"drug": drug_name, "products": []}

    products = []
    for r in results:
        products.append({
            "brand_name": r.get("brand_name", ""),
            "generic_name": r.get("generic_name", ""),
            "dosage_form": r.get("dosage_form", ""),
            "route": r.get("route", ""),
            "labeler_name": r.get("labeler_name", ""),
            "product_ndc": r.get("product_ndc", ""),
            "active_ingredients": r.get("active_ingredients", []),
        })
    return {"drug": drug_name, "products": products}


def _truncate_list(items: List[str], max_chars: int) -> List[str]:
    """Truncate long text items."""
    return [item[:max_chars] + "..." if len(item) > max_chars else item for item in items[:2]]


# --- FDA Drug Recalls (openFDA Enforcement API) ---


def fda_drug_recalls(
    drug_name: Optional[str] = None,
    classification: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """Search FDA drug recall/enforcement actions.

    Args:
        drug_name: Drug name to search (brand or generic). If None, returns recent recalls.
        classification: Filter by severity — 'Class I' (most serious), 'Class II', 'Class III'
        limit: Max results (1-25)

    Returns:
        Dict with recall events including reason, severity, status, and distribution
    """
    search_parts = []
    if drug_name:
        search_parts.append(
            f'(product_description:"{quote(drug_name)}"'
            f'+openfda.brand_name:"{quote(drug_name)}"'
            f'+openfda.generic_name:"{quote(drug_name)}")'
        )
    if classification:
        search_parts.append(f'classification:"{quote(classification)}"')

    search = "+AND+".join(search_parts) if search_parts else ""
    limit = min(max(limit, 1), 25)

    url = f"{FDA_BASE}/enforcement.json?"
    if search:
        url += f"search={search}&"
    url += f"sort=report_date:desc&limit={limit}"

    try:
        data = http.get(url, retries=2)
        results = data.get("results", [])

        recalls = []
        for r in results:
            openfda = r.get("openfda", {})
            recalls.append({
                "recall_number": r.get("recall_number", ""),
                "classification": r.get("classification", ""),
                "status": r.get("status", ""),
                "reason": r.get("reason_for_recall", ""),
                "product": r.get("product_description", "")[:300],
                "recalling_firm": r.get("recalling_firm", ""),
                "report_date": r.get("report_date", ""),
                "city": r.get("city", ""),
                "state": r.get("state", ""),
                "distribution": r.get("distribution_pattern", "")[:200],
                "brand_names": openfda.get("brand_name", []),
                "generic_names": openfda.get("generic_name", []),
            })

        return {
            "query": drug_name or "(recent recalls)",
            "classification_filter": classification,
            "total_found": data.get("meta", {}).get("results", {}).get("total", len(recalls)),
            "recalls": recalls,
        }

    except http.HTTPError as e:
        if e.status_code == 404:
            return {
                "query": drug_name or "(recent recalls)",
                "recalls": [],
                "message": "No recall events found",
            }
        raise


# --- Cost Plus Drugs Pricing (Mark Cuban Cost Plus Drug Company API) ---

COSTPLUS_BASE = "https://us-central1-costplusdrugs-publicapi.cloudfunctions.net/main"


def costplus_drug_price(
    drug_name: Optional[str] = None,
    brand_name: Optional[str] = None,
    quantity: Optional[int] = None,
    strength: Optional[str] = None,
) -> Dict[str, Any]:
    """Search Cost Plus Drugs for medication pricing.

    Args:
        drug_name: Generic drug name (e.g., "metformin")
        brand_name: Brand name (e.g., "Glucophage"). Sets generic_equivalent_ok=true.
        quantity: Number of units for a price quote (e.g., 30, 90)
        strength: Dosage strength filter (e.g., "500mg", "10mg")

    Returns:
        Dict with medication pricing info — unit price, total quote, form, strength, NDC
    """
    params = {}
    if drug_name:
        params["medication_name"] = drug_name
    if brand_name:
        params["brand_name"] = brand_name
        params["generic_equivalent_ok"] = "true"
    if quantity:
        params["quantity_units"] = str(quantity)
    if strength:
        params["strength"] = strength

    if not drug_name and not brand_name:
        return {"error": "Provide a drug name (generic or brand) to search"}

    url = f"{COSTPLUS_BASE}?{urlencode(params)}" if params else COSTPLUS_BASE

    try:
        data = http.get(url, retries=2, timeout=15)

        # API returns a list of medication objects
        medications = data if isinstance(data, list) else []

        if not medications:
            search_term = drug_name or brand_name
            return {
                "query": search_term,
                "medications": [],
                "message": f"'{search_term}' not found on Cost Plus Drugs. They carry ~2,300 mostly generic medications.",
            }

        results = []
        for med in medications[:10]:  # Cap at 10 results
            entry = {
                "name": med.get("medication_name", ""),
                "brand_name": med.get("brand_name", ""),
                "form": med.get("form", ""),
                "strength": med.get("strength", ""),
                "unit_price": med.get("unit_price", ""),
                "ndc": med.get("ndc", ""),
                "url": med.get("url", ""),
            }
            # Include quote if quantity was requested
            if quantity and med.get("requested_quote"):
                entry["total_quote"] = med.get("requested_quote", "")
                entry["quote_units"] = med.get("requested_quote_units", "")
            results.append(entry)

        return {
            "query": drug_name or brand_name,
            "quantity_requested": quantity,
            "strength_filter": strength,
            "count": len(results),
            "medications": results,
            "note": "Prices exclude ~$5.25 shipping. Cost Plus Drugs is mail-order only (3-5 day delivery).",
        }

    except http.HTTPError as e:
        return {
            "query": drug_name or brand_name,
            "error": f"Cost Plus Drugs API error: {e}",
        }


# --- ICD-10 Code Lookup (NLM API) ---

ICD10_BASE = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"


def icd10_lookup(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Search ICD-10-CM codes by description or code.

    Args:
        query: ICD-10 code or condition description
        max_results: Maximum results to return

    Returns:
        Dict with matched ICD-10 codes and descriptions
    """
    params = {"sf": "code,name", "terms": query, "maxList": str(max_results)}
    url = f"{ICD10_BASE}?{urlencode(params)}"

    try:
        data = http.get(url, retries=2)
        # Response is [total_count, codes, extra, [code, description] pairs]
        total = data[0] if len(data) > 0 else 0
        codes = data[3] if len(data) > 3 else []

        results = [{"code": c[0], "description": c[1]} for c in codes]
        return {"query": query, "total_matches": total, "codes": results}

    except (http.HTTPError, IndexError, KeyError) as e:
        return {"query": query, "error": str(e)}


# --- RxNorm Drug Interaction Check (NLM API) ---

RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"


def check_drug_interactions(drug_names: List[str]) -> Dict[str, Any]:
    """Check for drug-drug interactions using RxNorm + interaction API.

    Args:
        drug_names: List of drug names to check for interactions

    Returns:
        Dict with interaction data
    """
    # Step 1: Resolve drug names to RxCUI codes
    rxcuis = []
    resolved = {}
    for name in drug_names:
        url = f"{RXNORM_BASE}/rxcui.json?name={quote(name)}&search=1"
        try:
            data = http.get(url, retries=1)
            ids = data.get("idGroup", {}).get("rxnormId", [])
            if ids:
                rxcuis.append(ids[0])
                resolved[ids[0]] = name
        except http.HTTPError:
            pass

    if len(rxcuis) < 2:
        return {
            "drugs": drug_names,
            "error": f"Could only resolve {len(rxcuis)}/{len(drug_names)} drugs in RxNorm. Need at least 2.",
            "resolved": resolved,
        }

    # Step 2: Check interactions
    cui_str = "+".join(rxcuis)
    url = f"{RXNORM_BASE}/interaction/list.json?rxcuis={cui_str}"

    try:
        data = http.get(url, retries=2)
        interactions = []

        for group in data.get("fullInteractionTypeGroup", []):
            for itype in group.get("fullInteractionType", []):
                for pair in itype.get("interactionPair", []):
                    concepts = pair.get("interactionConcept", [])
                    drug_a = concepts[0].get("minConceptItem", {}).get("name", "") if len(concepts) > 0 else ""
                    drug_b = concepts[1].get("minConceptItem", {}).get("name", "") if len(concepts) > 1 else ""
                    interactions.append({
                        "drug_a": drug_a,
                        "drug_b": drug_b,
                        "severity": pair.get("severity", "N/A"),
                        "description": pair.get("description", ""),
                    })

        return {
            "drugs": drug_names,
            "interaction_count": len(interactions),
            "interactions": interactions,
        }

    except http.HTTPError as e:
        return {"drugs": drug_names, "error": str(e)}
