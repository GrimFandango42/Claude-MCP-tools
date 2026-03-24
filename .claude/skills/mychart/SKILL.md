---
name: mychart
version: "2.0.0"
description: "Patient-authorized access to MyChart/Epic health records via FHIR R4. 20+ data modes including labs, meds, conditions, vitals, immunizations, appointments, encounters, procedures, documents, coverage, care plans, goals, family history, and diagnostic reports. Clinical knowledge tools for FDA drug lookup, ICD-10 codes, and drug interaction checking. Supports multi-organization with OAuth2+PKCE."
argument-hint: 'mychart labs, mychart meds, mychart summary, mychart drug metformin, mychart icd10 diabetes, mychart interactions aspirin warfarin, mychart appointments, mychart immunizations, mychart encounters, mychart everything'
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
      - clinical-knowledge
      - drug-interactions
      - icd10
---

# MyChart v2.0.0: Patient Health Records via FHIR

> **Privacy notice**: This skill accesses your health records through Epic's FHIR API with your explicit authorization. Health data is processed during the conversation but NOT cached or stored locally. Only OAuth tokens and organization configs are persisted at `~/.local/share/mychart/mychart.db`.

Access your MyChart health records — labs, medications, conditions, allergies, vitals, immunizations, appointments, encounters, procedures, documents, coverage, care plans, goals, family history, and diagnostic reports — through Epic's FHIR R4 API with patient-authorized OAuth2 access. Also includes clinical knowledge tools (FDA drug info, ICD-10, drug interactions) that work without authentication.

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
| `immunizations` | Immunization history | Inline — see below |
| `appointments` | Appointments | Inline — see below |
| `procedures` | Procedure history | Inline — see below |
| `encounters` | Visit/encounter history | Inline — see below |
| `documents` | Clinical documents | Inline — see below |
| `coverage` | Insurance/coverage | Inline — see below |
| `careplans` | Care plans | Inline — see below |
| `goals` | Health goals | Inline — see below |
| `familyhistory` | Family medical history | Inline — see below |
| `diagnostics` | Diagnostic reports | Inline — see below |
| `everything` | All patient data ($everything) | Inline — see below |
| `lastn` | Latest observations ($lastn) | Inline — see below |
| `search` | Generic FHIR search | Inline — see below |
| `drug` | FDA drug lookup | Inline — no auth needed |
| `icd10` | ICD-10 code lookup | Inline — no auth needed |
| `interactions` | Drug interaction check | Inline — no auth needed |
| `patient` | Demographics | Inline — see below |
| `summary` | Full health overview | Inline — see below |

For `connect` or `orgs`: read the reference file and follow those instructions. **Do not continue below.**

For `drug`, `icd10`, `interactions`: these are **clinical knowledge tools** — they don't require MyChart authentication. Skip the pre-flight check.

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

This fetches conditions, allergies, medications, recent labs, recent vitals, immunizations, upcoming appointments, and coverage in one call. Synthesize into a comprehensive overview:

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

### Immunizations

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" immunizations --format compact --count 25
```

Synthesize: list each vaccine with date and status.

### Appointments

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" appointments --format compact
```

Shows future appointments by default. Add `--past` for all. Synthesize: show date, time, provider, location, and type.

### Procedures

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" procedures --format compact --count 20
```

Synthesize: list procedures with dates and outcomes.

### Encounters

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" encounters --format compact --count 20
```

Synthesize: show visit history — type, date, provider, reason.

### Documents

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" documents --format compact --count 10
```

Synthesize: list available clinical documents. Add `--doc-type <code>` to filter.

### Coverage

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" coverage --format compact --active-only
```

Synthesize: show insurance info — payor, plan, subscriber ID, period.

### Care Plans

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" careplans --format compact --active-only
```

Synthesize: list active care plans with activities.

### Goals

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" goals --format compact --active-only
```

Synthesize: show health goals with achievement status.

### Family History

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" familyhistory --format compact
```

Synthesize: list family medical history by relationship.

### Diagnostic Reports

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" diagnostics --format compact --count 10
```

Synthesize: show reports with conclusions and categories.

### Everything ($everything)

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" everything --format compact
```

Fetches ALL patient data in one call via FHIR `$everything`. Results grouped by resource type. Falls back to summary if server doesn't support the operation.

### Latest Observations ($lastn)

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" lastn --category vital-signs --max 1
```

Gets the latest observation per code. Categories: `vital-signs`, `laboratory`.

### Generic FHIR Search

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" search --type Observation --params category=laboratory code=2093-3
```

Search any FHIR resource type with custom parameters.

## Clinical Knowledge Tools (No Auth Required)

These tools use public FDA and NLM APIs — no MyChart connection needed.

### Drug Lookup

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" drug "metformin"
python3 "${SKILL_ROOT}/scripts/mychart.py" drug "lisinopril" --drug-type event
python3 "${SKILL_ROOT}/scripts/mychart.py" drug "atorvastatin" --drug-type ndc
```

Types: `label` (default — indications, warnings, dosage), `event` (top adverse events), `ndc` (product codes).

### ICD-10 Lookup

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" icd10 "diabetes"
python3 "${SKILL_ROOT}/scripts/mychart.py" icd10 "E11.9"
```

Search by condition name or ICD-10 code.

### Drug Interaction Checker

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" interactions aspirin warfarin
python3 "${SKILL_ROOT}/scripts/mychart.py" interactions metformin lisinopril atorvastatin
```

Checks drug-drug interactions via RxNorm. Provide 2+ drug names.

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
