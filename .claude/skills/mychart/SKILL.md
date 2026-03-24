---
name: mychart
version: "1.0.0"
description: "Patient-authorized access to MyChart/Epic health records via FHIR R4. Read labs, meds, conditions, vitals, appointments, and more. Supports multi-organization with OAuth2+PKCE."
argument-hint: 'mychart labs, mychart meds, mychart summary, mychart connect --sandbox, mychart allergies'
allowed-tools: Bash, Read, Write, AskUserQuestion
author: GrimFandango42
license: MIT
user-invocable: true
metadata:
  openclaw:
    emoji: "🏥"
    requires:
      optionalEnv:
        - EPIC_CLIENT_ID
      bins:
        - python3
    files:
      - "scripts/*"
    tags:
      - health
      - fhir
      - epic
      - mychart
      - medical-records
      - patient-data
      - labs
      - medications
      - ehr
---

# MyChart v1.0.0: Patient Health Records via FHIR

> **Privacy notice**: This skill accesses your health records through Epic's FHIR API with your explicit authorization. Health data is processed during the conversation but NOT cached or stored locally. Only OAuth tokens and organization configs are persisted at `~/.local/share/mychart/mychart.db`.

Access your MyChart health records — labs, medications, conditions, allergies, vitals, and more — through Epic's FHIR R4 API with patient-authorized OAuth2 access.

## Setup: Find Skill Root

```bash
for dir in \
  "." \
  "$HOME/.claude/skills/mychart" \
  "$HOME/.agents/skills/mychart"; do
  [ -n "$dir" ] && [ -f "$dir/scripts/mychart.py" ] && SKILL_ROOT="$dir" && break
done

if [ -z "${SKILL_ROOT:-}" ]; then
  echo "ERROR: Could not find scripts/mychart.py" >&2
  exit 1
fi
```

## Command Routing

Parse the user's first argument to determine the mode:

| First word | Mode | Handler |
|---|---|---|
| `connect` | OAuth setup | Read `${SKILL_ROOT}/references/connect.md`, follow instructions |
| `orgs` | Org management | Read `${SKILL_ROOT}/references/orgs.md`, follow instructions |
| `labs` | Lab results | Inline — see below |
| `meds` | Medications | Inline — see below |
| `conditions` | Conditions/diagnoses | Inline — see below |
| `allergies` | Allergies | Inline — see below |
| `vitals` | Vital signs | Inline — see below |
| `patient` | Demographics | Inline — see below |
| `summary` | Full health overview | Inline — see below |

For `connect` or `orgs`: read the reference file and follow those instructions. **Do not continue below.**

## Pre-flight: Check Connection

Before any data mode, verify the user is connected:

```bash
python3 "${SKILL_ROOT}/scripts/auth.py" status
```

If the output shows `"status": "no_orgs"` or all tokens are expired with no refresh:
- Tell the user: "You're not connected to MyChart yet. Let's set that up."
- Route to `references/connect.md`

If tokens are expired but refreshable, the data scripts handle refresh automatically.

## Data Modes (Inline)

All data modes use the same pattern:

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" <mode> [--format compact|json|markdown] [--count N] [--since YYYY-MM-DD] [--active-only]
```

Use a **timeout of 30000** (30 seconds) on the Bash call.

### Labs

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" labs --format compact --count 25
```

After getting results, synthesize for the user:
- Group by test type (CBC, metabolic panel, lipid panel, etc.)
- Highlight any abnormal flags
- Show trends if multiple results for the same test
- Note reference ranges

### Meds

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" meds --format compact --active-only
```

Synthesize:
- Group by category (cardiac, psychiatric, supplements, etc.)
- Show dosage and frequency
- Note the prescribing provider

### Conditions

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" conditions --format compact --active-only
```

Synthesize:
- List active conditions clearly
- Note onset dates
- Group by category if many

### Allergies

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" allergies --format compact
```

Synthesize:
- List each allergy/intolerance with reaction and severity
- Highlight any critical allergies

### Vitals

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" vitals --format compact --count 10
```

Synthesize:
- Show most recent readings for each vital type
- Note any readings outside normal range
- Show trends if multiple readings

### Patient

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" patient --format compact
```

Display basic demographics cleanly.

### Summary

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" summary --format compact
```

This fetches conditions, allergies, medications, recent labs, and recent vitals in one call. Synthesize into a comprehensive overview:

```
## Health Summary for [Name]

### Active Conditions
[List conditions]

### Allergies
[List allergies with severity]

### Current Medications
[List active meds with dosages]

### Recent Labs (last 30 days)
[Highlight abnormal results, trends]

### Recent Vitals
[Most recent BP, HR, weight, temp]
```

## Output Presentation

**CRITICAL**: Present health data clearly and accurately.

- Use the exact values from the FHIR data — do NOT approximate or round
- Always show units (mg/dL, mmHg, etc.)
- Flag abnormal results clearly
- Include dates for all results
- When showing trends, use actual data points, not summaries

**DO NOT**:
- Make clinical recommendations or diagnoses
- Interpret results beyond what the reference ranges indicate
- Suggest medication changes
- Provide medical advice

**DO**:
- Present data clearly and organized
- Highlight abnormal values factually
- Suggest the user discuss concerns with their healthcare provider
- Answer factual questions about what the data shows

## Error Handling

| Error | User Message |
|---|---|
| "Not connected" | "You're not connected to MyChart. Run `/mychart connect` to set up." |
| "Token expired" | "Your MyChart session has expired. Run `/mychart connect` to re-authenticate." |
| FHIR 403 | "Your health system doesn't provide access to this data type through the API." |
| FHIR 404 | "No [resource type] records found." |
| Network error | "Couldn't reach your health system's server. Check your connection and try again." |

## After Displaying Results

Offer follow-up options based on what was shown:
- If labs: "Want me to show trends for a specific test, or check your medications?"
- If meds: "Want me to look up any of these medications, or check your recent labs?"
- If summary: "Want to dive deeper into any section — labs, medications, or conditions?"

Stay in expert mode for the conversation — don't re-fetch data unless the user asks for a different mode or a refresh.
