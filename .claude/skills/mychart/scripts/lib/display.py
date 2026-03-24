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


def format_immunization(imm: Dict) -> Dict[str, str]:
    """Format an Immunization resource."""
    return {
        "vaccine": _coding_display(imm.get("vaccineCode")),
        "date": _date(imm.get("occurrenceDateTime", imm.get("occurrenceString", ""))),
        "status": imm.get("status", ""),
        "site": _coding_display(imm.get("site")),
        "lot": imm.get("lotNumber", ""),
    }


def format_appointment(appt: Dict) -> Dict[str, str]:
    """Format an Appointment resource."""
    participants = appt.get("participant", [])
    provider = ""
    location = ""
    for p in participants:
        actor = p.get("actor", {})
        ref = actor.get("reference", "")
        display = actor.get("display", "")
        if "Practitioner" in ref:
            provider = display
        elif "Location" in ref:
            location = display

    return {
        "date": _date(appt.get("start", "")),
        "time": appt.get("start", "")[11:16] if len(appt.get("start", "")) > 11 else "",
        "status": appt.get("status", ""),
        "type": _coding_display(appt.get("appointmentType")) or _coding_display((appt.get("serviceType") or [{}])[0]),
        "provider": provider,
        "location": location,
        "minutes": str(appt.get("minutesDuration", "")) if appt.get("minutesDuration") else "",
        "description": appt.get("description", ""),
    }


def format_procedure(proc: Dict) -> Dict[str, str]:
    """Format a Procedure resource."""
    performed = proc.get("performedDateTime", "")
    if not performed:
        performed = _safe(proc, "performedPeriod", "start")
    return {
        "procedure": _coding_display(proc.get("code")),
        "date": _date(performed),
        "status": proc.get("status", ""),
        "outcome": _coding_display(proc.get("outcome")),
    }


def format_encounter(enc: Dict) -> Dict[str, str]:
    """Format an Encounter resource."""
    period = enc.get("period", {})
    participants = enc.get("participant", [])
    provider = ""
    for p in participants:
        individual = p.get("individual", {})
        if individual.get("display"):
            provider = individual["display"]
            break
    enc_class = enc.get("class", {})
    class_display = _coding_display(enc_class) if isinstance(enc_class, dict) else str(enc_class)
    return {
        "type": _coding_display((enc.get("type") or [{}])[0]),
        "class": class_display,
        "start": _date(period.get("start", "")),
        "end": _date(period.get("end", "")),
        "status": enc.get("status", ""),
        "provider": provider,
        "reason": _coding_display((enc.get("reasonCode") or [{}])[0]),
    }


def format_document_ref(doc: Dict) -> Dict[str, str]:
    """Format a DocumentReference resource."""
    content = doc.get("content", [])
    content_type = ""
    url = ""
    if content:
        attachment = content[0].get("attachment", {})
        content_type = attachment.get("contentType", "")
        url = attachment.get("url", "")
    return {
        "title": doc.get("description", "") or _coding_display(doc.get("type")),
        "type": _coding_display(doc.get("type")),
        "date": _date(doc.get("date", "")),
        "status": doc.get("status", ""),
        "format": content_type,
        "url": url,
    }


def format_coverage(cov: Dict) -> Dict[str, str]:
    """Format a Coverage resource."""
    payor = cov.get("payor", [])
    payor_display = payor[0].get("display", "") if payor else ""
    return {
        "payor": payor_display,
        "type": _coding_display(cov.get("type")),
        "subscriber_id": cov.get("subscriberId", ""),
        "status": cov.get("status", ""),
        "period_start": _date(_safe(cov, "period", "start")),
        "period_end": _date(_safe(cov, "period", "end")),
        "relationship": _coding_display(cov.get("relationship")),
    }


def format_care_plan(cp: Dict) -> Dict[str, str]:
    """Format a CarePlan resource."""
    activities = cp.get("activity", [])
    activity_list = []
    for a in activities[:3]:
        detail = a.get("detail", {})
        activity_list.append(_coding_display(detail.get("code")) or detail.get("description", ""))
    return {
        "title": cp.get("title", "") or _coding_display((cp.get("category") or [{}])[0]),
        "status": cp.get("status", ""),
        "intent": cp.get("intent", ""),
        "period_start": _date(_safe(cp, "period", "start")),
        "period_end": _date(_safe(cp, "period", "end")),
        "activities": "; ".join(a for a in activity_list if a),
    }


def format_goal(goal: Dict) -> Dict[str, str]:
    """Format a Goal resource."""
    target = (goal.get("target") or [{}])[0]
    desc = goal.get("description", {})
    return {
        "description": _coding_display(desc) if isinstance(desc, dict) else str(desc),
        "status": goal.get("lifecycleStatus", ""),
        "achievement": _coding_display(goal.get("achievementStatus")),
        "start_date": _date(goal.get("startDate", "")),
        "target_date": _date(target.get("dueDate", "")),
        "category": _coding_display((goal.get("category") or [{}])[0]),
    }


def format_family_history(fh: Dict) -> Dict[str, str]:
    """Format a FamilyMemberHistory resource."""
    conditions = fh.get("condition", [])
    cond_text = "; ".join(_coding_display(c.get("code")) for c in conditions[:3])
    return {
        "relationship": _coding_display(fh.get("relationship")),
        "sex": _coding_display(fh.get("sex")),
        "conditions": cond_text,
        "deceased": str(fh.get("deceasedBoolean", "")) if "deceasedBoolean" in fh else "",
    }


def format_diagnostic_report(dr: Dict) -> Dict[str, str]:
    """Format a DiagnosticReport resource."""
    return {
        "report": _coding_display(dr.get("code")),
        "status": dr.get("status", ""),
        "date": _date(dr.get("effectiveDateTime", _safe(dr, "effectivePeriod", "start"))),
        "category": _coding_display((dr.get("category") or [{}])[0]),
        "conclusion": dr.get("conclusion", ""),
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
        "Immunization": format_immunization,
        "Appointment": format_appointment,
        "Procedure": format_procedure,
        "Encounter": format_encounter,
        "DocumentReference": format_document_ref,
        "Coverage": format_coverage,
        "CarePlan": format_care_plan,
        "Goal": format_goal,
        "FamilyMemberHistory": format_family_history,
        "DiagnosticReport": format_diagnostic_report,
    }

    formatter = formatters.get(resource_type)
    if not formatter:
        # Generic fallback — extract key fields from any FHIR resource
        return _format_generic(resources, mode)

    formatted = [formatter(r) for r in resources]

    if mode == "markdown":
        return _to_markdown_table(formatted)
    else:
        return _to_compact(formatted, resource_type)


def _format_generic(resources: List[Dict], mode: str) -> str:
    """Generic formatter for any FHIR resource type — extracts key fields."""
    items = []
    for r in resources:
        item = {}
        rt = r.get("resourceType", "Resource")
        item["type"] = rt
        # Extract common high-value fields
        if r.get("code"):
            item["code"] = _coding_display(r["code"])
        if r.get("text", {}).get("div"):
            # Strip HTML from narrative
            text = r["text"]["div"]
            import re
            item["text"] = re.sub(r"<[^>]+>", "", text)[:200]
        for key in ("status", "intent", "description", "name"):
            if r.get(key) and isinstance(r[key], str):
                item[key] = r[key]
        if r.get("effectiveDateTime"):
            item["date"] = _date(r["effectiveDateTime"])
        elif r.get("date"):
            item["date"] = _date(r["date"])
        items.append(item)

    if mode == "markdown":
        return _to_markdown_table(items)
    rtype = resources[0].get("resourceType", "Resource") if resources else "Resource"
    return _to_compact(items, rtype)


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
