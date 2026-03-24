"""Output formatters for FHIR resources.

Extracts clinically meaningful fields from raw FHIR JSON
and formats them for Claude synthesis or user display.
Includes canvas card renderers for the onboarding wizard.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


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


# --- Canvas Card Renderers (Onboarding Wizard) ---


def render_welcome_card() -> str:
    """Render the onboarding welcome card with capability overview."""
    return """### Welcome to MyChart

Access your health records and medical reference tools — all from here.

**No sign-in needed:**
| Tool | What it does |
|------|-------------|
| Drug Lookup | Search FDA database for any medication — indications, warnings, side effects |
| ICD-10 Codes | Look up diagnosis codes by name or code |
| Drug Interactions | Check interactions between 2+ medications |

**After connecting your health system:**
| Category | What you can access |
|----------|-------------------|
| Lab Results | Blood work, metabolic panels, lipids — with trends over time |
| Medications | Current prescriptions with dosages and prescribers |
| Conditions | Active diagnoses and health conditions |
| Vitals | Blood pressure, heart rate, weight, temperature |
| Allergies | Known allergies with reaction details and severity |
| Immunizations | Vaccination history and status |
| Appointments | Upcoming and past visits |
| And more... | Encounters, procedures, documents, coverage, care plans, goals, family history |

---
**What would you like to do?**
1. Try a drug lookup right now (no sign-in needed)
2. Connect my health system
3. Just exploring — tell me more"""


def render_progress_tracker(
    current_step: int,
    total_steps: int,
    title: str,
    items: List[Tuple[str, bool]],
) -> str:
    """Render a step progress tracker.

    Args:
        current_step: Current step number (1-based)
        total_steps: Total number of steps
        title: Title for the current step
        items: List of (label, completed) tuples for checklist items
    """
    progress = f"Step {current_step} of {total_steps}"
    bar_filled = current_step
    bar_empty = total_steps - current_step
    bar = "[" + "=" * bar_filled + "." * bar_empty + "]"

    lines = [f"### {title}", f"{bar} {progress}", ""]
    for label, done in items:
        check = "x" if done else " "
        lines.append(f"- [{check}] {label}")
    return "\n".join(lines)


def render_drug_card(data: Dict[str, Any]) -> str:
    """Render a drug lookup result as a formatted card.

    Args:
        data: Dict with keys like brand_name, generic_name, drug_class,
              route, indications, warnings (list)
    """
    name = data.get("brand_name") or data.get("generic_name", "Unknown Drug")
    lines = [f"### {name}", ""]
    lines.append("| Field | Details |")
    lines.append("|-------|---------|")

    field_map = [
        ("Generic Name", "generic_name"),
        ("Brand Names", "brand_name"),
        ("Drug Class", "drug_class"),
        ("Route", "route"),
        ("Indications", "indications"),
    ]
    for label, key in field_map:
        val = data.get(key, "")
        if val:
            display = str(val)[:200]
            lines.append(f"| **{label}** | {display} |")

    warnings = data.get("warnings", [])
    if warnings:
        lines.append("")
        lines.append("**Key Warnings:**")
        for w in warnings[:3]:
            lines.append(f"- {str(w)[:150]}")

    return "\n".join(lines)


def render_connection_status(
    state: str,
    details: Optional[Dict[str, str]] = None,
) -> str:
    """Render an auth connection status card.

    Args:
        state: One of 'connecting', 'awaiting', 'success', 'error'
        details: Optional dict with org, patient_id, expiry, error, auth_url
    """
    details = details or {}

    if state == "connecting":
        org = details.get("org", "your health system")
        return render_progress_tracker(3, 5, f"Connecting to {org}...", [
            ("Found endpoint", True),
            ("Security handshake prepared", True),
            ("Waiting for sign-in via browser...", False),
        ])

    if state == "awaiting":
        lines = ["### Waiting for Sign-In", ""]
        lines.append("A browser window should have opened. Sign in with your MyChart credentials.")
        if details.get("auth_url"):
            lines.append("\n> Browser didn't open? Use this link to sign in manually.")
        return "\n".join(lines)

    if state == "success":
        lines = ["### Connected!", ""]
        lines.append("| Detail | Value |")
        lines.append("|--------|-------|")
        for label, key in [
            ("Health System", "org"),
            ("Patient ID", "patient_id"),
            ("Session expires", "expiry"),
            ("Available data", "scopes"),
        ]:
            val = details.get(key, "")
            if val:
                lines.append(f"| {label} | {val} |")
        return "\n".join(lines)

    if state == "error":
        error = details.get("error", "Unknown error")
        return f"### Connection Error\n\n{error}\n\n> Want to try again, or explore the clinical tools (drug lookup, ICD-10) instead?"

    return ""


def render_insurance_review(fields: Dict[str, Tuple[str, str]]) -> str:
    """Render parsed insurance card fields for user confirmation.

    Args:
        fields: Dict mapping field name to (value, confidence) tuples.
               confidence is 'high', 'medium', or 'low'.
    """
    lines = ["### Insurance Card — Review", ""]
    lines.append("| Field | Parsed Value | Confidence |")
    lines.append("|-------|-------------|------------|")

    conf_display = {"high": "High", "medium": "Medium", "low": "Low"}
    for name, (value, confidence) in fields.items():
        conf = conf_display.get(confidence, confidence)
        lines.append(f"| {name} | {value} | {conf} |")

    lines.extend([
        "",
        "**Does this look right?**",
        "1. Yes — save it",
        "2. I need to fix something",
        "3. Discard — don't save",
    ])
    return "\n".join(lines)


def render_health_snapshot(data: Dict[str, Any]) -> str:
    """Render a health dashboard from summary data.

    Args:
        data: Dict with keys: conditions, medications, labs, vitals,
              allergies, appointments, patient_name
    """
    now = datetime.now()
    month_year = now.strftime("%B %Y")
    name = data.get("patient_name", "Patient")

    lines = [f"### Your Health Snapshot — {month_year}", ""]

    conditions = data.get("conditions", [])
    if conditions:
        lines.append("**Active Conditions**")
        for c in conditions:
            onset = f" (onset: {c['onset']})" if c.get("onset") else ""
            lines.append(f"- {c.get('condition', 'Unknown')}{onset}")
        lines.append("")

    meds = data.get("medications", [])
    if meds:
        lines.append(f"**Current Medications** ({len(meds)})")
        lines.append("| Medication | Dosage | Status |")
        lines.append("|-----------|--------|--------|")
        for m in meds:
            lines.append(f"| {m.get('drug', '')} | {m.get('dosage', '')} | {m.get('status', '')} |")
        lines.append("")

    labs = data.get("labs", [])
    if labs:
        lines.append("**Recent Labs**")
        lines.append("| Test | Value | Range | Flag |")
        lines.append("|------|-------|-------|------|")
        for lab in labs:
            flag = lab.get("flag", "")
            lines.append(f"| {lab.get('test', '')} | {lab.get('value', '')} | {lab.get('range', '')} | {flag} |")
        lines.append("")

    vitals = data.get("vitals", [])
    if vitals:
        lines.append("**Recent Vitals**")
        lines.append("| Vital | Reading | Date |")
        lines.append("|-------|---------|------|")
        for v in vitals:
            lines.append(f"| {v.get('type', '')} | {v.get('value', '')} | {v.get('date', '')} |")
        lines.append("")

    allergies = data.get("allergies", [])
    if allergies:
        lines.append("**Allergies**")
        for a in allergies:
            crit = f" ({a['criticality']})" if a.get("criticality") else ""
            lines.append(f"- {a.get('substance', 'Unknown')}{crit}")
        lines.append("")

    appts = data.get("appointments", [])
    if appts:
        lines.append("**Upcoming Appointments**")
        lines.append("| Date | Provider | Type |")
        lines.append("|------|----------|------|")
        for a in appts:
            lines.append(f"| {a.get('date', '')} | {a.get('provider', '')} | {a.get('type', '')} |")
        lines.append("")

    lines.append("> **Dive deeper:** `labs` `meds` `vitals` `conditions` `appointments` `summary`")
    return "\n".join(lines)


def render_quick_reference() -> str:
    """Render the post-onboarding command reference card."""
    return """### You're all set!

| Command | What it does |
|---------|-------------|
| `/mychart labs` | Recent lab results with trends |
| `/mychart meds` | Current medications |
| `/mychart conditions` | Active diagnoses |
| `/mychart vitals` | Blood pressure, weight, etc. |
| `/mychart allergies` | Allergy list |
| `/mychart appointments` | Upcoming visits |
| `/mychart summary` | Full health overview |
| `/mychart drug [name]` | Look up any medication |
| `/mychart interactions [d1] [d2]` | Check drug interactions |
| `/mychart icd10 [term]` | Look up diagnosis codes |
| `/mychart connect [org]` | Add another health system |
| `/mychart setup` | Re-run this wizard |

Just ask — I can pull up any of your health data anytime."""
