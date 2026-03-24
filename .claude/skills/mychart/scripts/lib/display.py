"""Output formatters for FHIR resources.

Extracts clinically meaningful fields from raw FHIR JSON
and formats them for Claude synthesis or user display.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


def _safe(resource: Dict, *keys: str, default: str = "") -> str:
    """Safely extract nested value from FHIR resource."""
    val = resource
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        elif isinstance(val, list) and val:
            val = val[0]
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
        else:
            return default
    return str(val) if val is not None else default


def _date(iso: Optional[str]) -> str:
    """Format ISO date to readable string."""
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return iso[:10] if len(iso) >= 10 else iso


def _coding_display(codeable_concept: Optional[Dict]) -> str:
    """Extract display text from a CodeableConcept."""
    if not codeable_concept:
        return ""
    if codeable_concept.get("text"):
        return codeable_concept["text"]
    codings = codeable_concept.get("coding", [])
    for c in codings:
        if c.get("display"):
            return c["display"]
    return ""


# --- Resource Formatters ---


def format_observation_lab(obs: Dict) -> Dict[str, str]:
    """Format a lab result Observation."""
    value = ""
    unit = ""
    if "valueQuantity" in obs:
        vq = obs["valueQuantity"]
        value = str(vq.get("value", ""))
        unit = vq.get("unit", vq.get("code", ""))
    elif "valueString" in obs:
        value = obs["valueString"]
    elif "valueCodeableConcept" in obs:
        value = _coding_display(obs["valueCodeableConcept"])

    # Reference range
    ref_range = ""
    ranges = obs.get("referenceRange", [])
    if ranges:
        r = ranges[0]
        low = r.get("low", {}).get("value", "")
        high = r.get("high", {}).get("value", "")
        if low and high:
            ref_range = f"{low}-{high}"
        elif low:
            ref_range = f">={low}"
        elif high:
            ref_range = f"<={high}"
        if r.get("text"):
            ref_range = r["text"]

    # Abnormal flag
    interpretation = ""
    interps = obs.get("interpretation", [])
    for i in interps:
        interpretation = _coding_display(i)

    return {
        "test": _coding_display(obs.get("code")),
        "value": f"{value} {unit}".strip(),
        "range": ref_range,
        "flag": interpretation,
        "date": _date(obs.get("effectiveDateTime", obs.get("issued"))),
        "status": obs.get("status", ""),
    }


def format_observation_vital(obs: Dict) -> Dict[str, str]:
    """Format a vital sign Observation."""
    # Handle component observations (e.g., blood pressure has systolic + diastolic)
    components = obs.get("component", [])
    if components:
        parts = []
        for comp in components:
            name = _coding_display(comp.get("code"))
            vq = comp.get("valueQuantity", {})
            val = vq.get("value", "")
            unit = vq.get("unit", "")
            parts.append(f"{name}: {val} {unit}".strip())
        value = " / ".join(parts)
    else:
        vq = obs.get("valueQuantity", {})
        value = f"{vq.get('value', '')} {vq.get('unit', '')}".strip()

    return {
        "type": _coding_display(obs.get("code")),
        "value": value,
        "date": _date(obs.get("effectiveDateTime")),
        "status": obs.get("status", ""),
    }


def format_medication(med: Dict) -> Dict[str, str]:
    """Format a MedicationRequest."""
    drug = _coding_display(med.get("medicationCodeableConcept"))
    if not drug:
        ref = med.get("medicationReference", {})
        drug = ref.get("display", "")

    dosage = ""
    dosages = med.get("dosageInstruction", [])
    if dosages:
        d = dosages[0]
        dosage = d.get("text", "")
        if not dosage:
            parts = []
            for dr in d.get("doseAndRate", []):
                dq = dr.get("doseQuantity", {})
                if dq:
                    parts.append(f"{dq.get('value', '')} {dq.get('unit', '')}".strip())
            timing = d.get("timing", {})
            if timing.get("code"):
                parts.append(_coding_display(timing["code"]))
            elif timing.get("repeat"):
                rep = timing["repeat"]
                freq = rep.get("frequency", "")
                period = rep.get("period", "")
                period_unit = rep.get("periodUnit", "")
                if freq and period:
                    parts.append(f"{freq}x per {period} {period_unit}".strip())
            dosage = " ".join(parts)

    requester = ""
    req = med.get("requester", {})
    if req:
        requester = req.get("display", "")

    return {
        "drug": drug,
        "dosage": dosage,
        "status": med.get("status", ""),
        "intent": med.get("intent", ""),
        "date": _date(med.get("authoredOn")),
        "prescriber": requester,
    }


def format_condition(cond: Dict) -> Dict[str, str]:
    """Format a Condition resource."""
    clinical_status = _coding_display(cond.get("clinicalStatus"))
    verification = _coding_display(cond.get("verificationStatus"))
    onset = cond.get("onsetDateTime", "")
    if not onset:
        onset = _safe(cond, "onsetPeriod", "start")

    return {
        "condition": _coding_display(cond.get("code")),
        "status": clinical_status,
        "verification": verification,
        "onset": _date(onset),
        "category": _coding_display(cond.get("category", [{}])[0]) if cond.get("category") else "",
    }


def format_allergy(allergy: Dict) -> Dict[str, str]:
    """Format an AllergyIntolerance resource."""
    reactions = allergy.get("reaction", [])
    reaction_text = ""
    if reactions:
        manifestations = reactions[0].get("manifestation", [])
        reaction_text = ", ".join(_coding_display(m) for m in manifestations)

    return {
        "substance": _coding_display(allergy.get("code")),
        "type": allergy.get("type", ""),
        "category": ", ".join(allergy.get("category", [])),
        "criticality": allergy.get("criticality", ""),
        "reaction": reaction_text,
        "status": _coding_display(allergy.get("clinicalStatus")),
    }


# --- Output Modes ---


def format_resources(
    resources: List[Dict], resource_type: str, mode: str = "compact"
) -> str:
    """Format a list of FHIR resources for output.

    Args:
        resources: List of FHIR resource dicts
        resource_type: FHIR resource type name
        mode: 'compact' (for Claude), 'json' (raw), 'markdown' (tables)
    """
    if mode == "json":
        return json.dumps(resources, indent=2)

    # Choose formatter
    formatters = {
        "Observation:laboratory": format_observation_lab,
        "Observation:vital-signs": format_observation_vital,
        "MedicationRequest": format_medication,
        "Condition": format_condition,
        "AllergyIntolerance": format_allergy,
    }

    formatter = formatters.get(resource_type)
    if not formatter:
        # Generic fallback
        if mode == "compact":
            return json.dumps(resources, indent=2)
        return json.dumps(resources, indent=2)

    formatted = [formatter(r) for r in resources]

    if mode == "markdown":
        return _to_markdown_table(formatted)
    else:
        return _to_compact(formatted, resource_type)


def _to_compact(items: List[Dict[str, str]], resource_type: str) -> str:
    """Compact output for Claude synthesis."""
    lines = [f"## {resource_type} ({len(items)} results)"]
    for item in items:
        parts = [f"{k}={v}" for k, v in item.items() if v]
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def _to_markdown_table(items: List[Dict[str, str]]) -> str:
    """Markdown table output."""
    if not items:
        return "No results."

    headers = list(items[0].keys())
    lines = ["| " + " | ".join(h.title() for h in headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for item in items:
        row = "| " + " | ".join(item.get(h, "") for h in headers) + " |"
        lines.append(row)
    return "\n".join(lines)
