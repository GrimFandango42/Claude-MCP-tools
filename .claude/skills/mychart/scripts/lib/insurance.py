"""Insurance card parsing and wizard logic.

Extracts insurance details from free text or generates prompts
for Claude to parse insurance card images.
"""

import re
from typing import Dict, List, Optional


# --- Known Payors ---

KNOWN_PAYORS = {
    "UnitedHealthcare": ["UHC", "United Healthcare", "United Health", "UnitedHealth", "Optum"],
    "Blue Cross Blue Shield": ["BCBS", "Blue Cross", "Blue Shield", "BlueCross", "BlueShield"],
    "Anthem": ["Anthem", "Elevance", "Anthem BCBS", "Anthem Blue Cross"],
    "Aetna": ["Aetna", "CVS/Aetna", "CVS Aetna", "Aetna CVS Health"],
    "Cigna": ["Cigna", "Evernorth", "Cigna Healthcare"],
    "Humana": ["Humana", "Humana Inc"],
    "Kaiser Permanente": ["Kaiser", "KP", "Kaiser Permanente"],
    "Centene": ["Centene", "Ambetter", "WellCare", "Wellcare"],
    "Molina Healthcare": ["Molina", "Molina Healthcare"],
    "Health Care Service Corporation": ["HCSC"],
    "Highmark": ["Highmark", "Highmark BCBS"],
    "CVS Health": ["CVS Health", "CVS Caremark"],
    "Independence Blue Cross": ["IBX", "Independence", "Independence Blue Cross"],
    "CareFirst": ["CareFirst", "CareFirst BCBS"],
    "Premera Blue Cross": ["Premera", "Premera Blue Cross"],
    "Regence": ["Regence", "Regence BCBS"],
    "Oscar Health": ["Oscar", "Oscar Health"],
    "Bright Health": ["Bright Health", "Bright HealthCare"],
    "Clover Health": ["Clover", "Clover Health"],
    "Devoted Health": ["Devoted", "Devoted Health"],
    "Medicare": ["Medicare", "CMS", "Original Medicare"],
    "Medicaid": ["Medicaid", "State Medicaid"],
    "Tricare": ["Tricare", "TRICARE"],
    "Veterans Affairs": ["VA", "Veterans Affairs", "VA Health"],
    "Emblem Health": ["Emblem", "EmblemHealth", "GHI", "HIP"],
    "Geisinger": ["Geisinger", "Geisinger Health Plan"],
    "Priority Health": ["Priority Health"],
    "HAP": ["HAP", "Health Alliance Plan"],
    "HealthPartners": ["HealthPartners"],
    "Tufts Health Plan": ["Tufts", "Tufts Health", "Point32Health"],
}

# Flatten for lookup
_PAYOR_LOOKUP = {}
for canonical, variations in KNOWN_PAYORS.items():
    _PAYOR_LOOKUP[canonical.lower()] = canonical
    for v in variations:
        _PAYOR_LOOKUP[v.lower()] = canonical

PLAN_TYPES = {"HMO", "PPO", "EPO", "POS", "HDHP", "HSA", "FSA", "PPA", "PFFS", "SNP"}


def normalize_payor(name: str) -> str:
    """Match input against known payors, return canonical name."""
    name_lower = name.strip().lower()

    # Direct match
    if name_lower in _PAYOR_LOOKUP:
        return _PAYOR_LOOKUP[name_lower]

    # Substring match — find best (longest) match
    best_match = None
    best_len = 0
    for key, canonical in _PAYOR_LOOKUP.items():
        if key in name_lower and len(key) > best_len:
            best_match = canonical
            best_len = len(key)

    return best_match or name.strip()


def parse_insurance_text(text: str) -> Dict:
    """Parse free-text insurance info into structured fields.

    Returns dict with extracted fields and confidence levels.
    """
    result = {"raw_text": text, "fields": {}, "confidence": {}}
    fields = result["fields"]
    confidence = result["confidence"]

    payor = _extract_payor(text)
    if payor:
        fields["payor"] = payor
        confidence["payor"] = "high" if payor in KNOWN_PAYORS else "medium"

    plan_type = _extract_plan_type(text)
    if plan_type:
        fields["plan_type"] = plan_type
        confidence["plan_type"] = "high"

    member_id = _extract_member_id(text)
    if member_id:
        fields["member_id"] = member_id
        confidence["member_id"] = "high" if _has_label(text, member_id, ["member", "id", "subscriber"]) else "medium"

    group = _extract_group(text)
    if group:
        fields["group_number"] = group
        confidence["group_number"] = "high" if _has_label(text, group, ["group", "grp"]) else "medium"

    phones = _extract_phones(text)
    if phones:
        fields["phone"] = phones[0]
        confidence["phone"] = "high"
        if len(phones) > 1:
            fields["additional_phones"] = phones[1:]

    plan_name = _extract_plan_name(text, payor, plan_type)
    if plan_name:
        fields["plan_name"] = plan_name
        confidence["plan_name"] = "medium"

    rxbin = _extract_labeled(text, ["rxbin", "rx bin", "bin"])
    if rxbin:
        fields["rx_bin"] = rxbin
        confidence["rx_bin"] = "high"

    rxpcn = _extract_labeled(text, ["rxpcn", "rx pcn", "pcn"])
    if rxpcn:
        fields["rx_pcn"] = rxpcn
        confidence["rx_pcn"] = "high"

    rxgrp = _extract_labeled(text, ["rxgrp", "rx grp", "rx group"])
    if rxgrp:
        fields["rx_group"] = rxgrp
        confidence["rx_group"] = "high"

    return result


def parse_insurance_image_prompt(image_path: str) -> str:
    """Return a prompt for Claude to extract insurance info from a card image."""
    return f"""Examine this insurance card image and extract ALL of the following. For each field, provide the exact text as shown on the card:

1. **Insurance Company / Payor**
2. **Plan Name** (e.g., "Gold PPO", "Choice Plus")
3. **Plan Type** (HMO, PPO, EPO, POS, HDHP, or other)
4. **Member ID**
5. **Group Number**
6. **Subscriber Name**
7. **Effective Date**
8. **Copay amounts** (PCP, specialist, ER, Urgent Care, Rx)
9. **Deductible** (individual and/or family)
10. **RxBIN**
11. **RxPCN**
12. **RxGroup**
13. **Customer Service Phone**
14. **Other Phone Numbers** (mental health, pharmacy, nurse line)
15. **Network** (e.g., "First Health Network", "Cigna Open Access")

If a field is not visible, write "Not shown". If text is partially obscured, note what you can read and mark uncertain.

Image: {image_path}"""


# --- Internal extraction helpers ---

def _extract_payor(text: str) -> Optional[str]:
    """Find insurance company name in text."""
    text_lower = text.lower()
    best_match = None
    best_len = 0
    for key, canonical in _PAYOR_LOOKUP.items():
        if key in text_lower and len(key) > best_len:
            best_match = canonical
            best_len = len(key)
    return best_match


def _extract_plan_type(text: str) -> Optional[str]:
    """Find plan type (HMO, PPO, etc.)."""
    text_upper = text.upper()
    for pt in PLAN_TYPES:
        if re.search(rf'\b{pt}\b', text_upper):
            return pt
    return None


def _extract_member_id(text: str) -> Optional[str]:
    """Extract member/subscriber ID."""
    labeled = _extract_labeled(text, [
        "member id", "member #", "memberid", "member number",
        "subscriber id", "subscriber #", "subscriberid",
        "id number", "id #", "id:",
    ])
    if labeled:
        return labeled
    # Fallback: alphanumeric strings 8-15 chars
    candidates = re.findall(r'\b[A-Z0-9]{8,15}\b', text.upper())
    for c in candidates:
        if not re.match(r'^\d{10,}$', c):  # Not a phone number
            return c
    return None


def _extract_group(text: str) -> Optional[str]:
    """Extract group number."""
    return _extract_labeled(text, [
        "group #", "group:", "group number", "grp #", "grp:", "grp",
    ])


def _extract_phones(text: str) -> List[str]:
    """Extract phone numbers."""
    phones = []
    for match in re.finditer(r'1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text):
        phone = re.sub(r'[^\d]', '', match.group())
        if len(phone) >= 10:
            if len(phone) == 11 and phone[0] == '1':
                phone = phone[1:]
            formatted = f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
            if formatted not in phones:
                phones.append(formatted)
    return phones


def _extract_labeled(text: str, labels: List[str]) -> Optional[str]:
    """Extract value following a label."""
    text_lower = text.lower()
    for label in labels:
        idx = text_lower.find(label)
        if idx >= 0:
            after = text[idx + len(label):].strip()
            after = re.sub(r'^[:#\s]+', '', after)
            match = re.match(r'([A-Za-z0-9][\w\-\.]{2,20})', after)
            if match:
                return match.group(1)
    return None


def _extract_plan_name(text: str, payor: Optional[str], plan_type: Optional[str]) -> Optional[str]:
    """Try to extract plan name from text."""
    for line in text.split('\n'):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        has_payor = payor and payor.lower() in line.lower()
        has_type = plan_type and plan_type in line.upper()
        if has_payor or has_type:
            cleaned = re.sub(r'\s+', ' ', line_stripped)
            if 5 < len(cleaned) < 80:
                return cleaned
    return None


def _has_label(text: str, value: str, keywords: List[str]) -> bool:
    """Check if a value appears near a label keyword."""
    text_lower = text.lower()
    val_idx = text_lower.find(value.lower())
    if val_idx < 0:
        return False
    context = text_lower[max(0, val_idx - 50):val_idx]
    return any(kw in context for kw in keywords)
