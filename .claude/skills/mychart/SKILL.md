---
name: mychart
version: "2.1.0"
description: "Patient health companion — MyChart records via FHIR R4, FDA drug/recall data, ICD-10 codes, drug interactions, hospital quality ratings, provider search, and clinical trials. 27 modes organized by what you need: understand results, manage ongoing care, research & plan, or navigate the system."
argument-hint: 'mychart setup, mychart labs, mychart meds, mychart summary, mychart drug metformin, mychart recalls metformin, mychart icd10 diabetes, mychart interactions aspirin warfarin, mychart providers --specialty Cardiology --zip-code 90210, mychart hospitals --state CA --city "Los Angeles", mychart trials "type 2 diabetes", mychart appointments, mychart everything'
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
      - drug-recalls
      - hospital-quality
      - icd10
---

# MyChart v2.1.0: Patient Health Companion

> **Privacy notice**: This skill accesses your health records through Epic's FHIR API with your explicit authorization. Health data is processed during the conversation but NOT cached or stored locally. Only OAuth tokens and organization configs are persisted at `~/.local/share/mychart/mychart.db`.

27 commands organized by what you're trying to do — from understanding new lab results to finding the best-rated hospital near you. Connects to MyChart/Epic via FHIR R4 for your records, plus public FDA, CMS, NLM, and NPI APIs for clinical knowledge (no login needed).

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

## Mode Detection & Routing

Detect what the user needs based on their first argument. Commands are grouped by user intent — use this to offer relevant follow-ups.

### Account & Setup (run reference files, then stop)

| Command | What it does | Handler |
|---|---|---|
| `setup` | First-time onboarding wizard | Read `${SKILL_ROOT}/references/onboarding.md` |
| `connect` | OAuth authorization flow | Read `${SKILL_ROOT}/references/connect.md` |
| `orgs` | Manage connected organizations | Read `${SKILL_ROOT}/references/orgs.md` |

For these: read the reference file and follow those instructions. **Do not continue below.**

### "Understand What Just Happened" (interpret results, research a diagnosis or medication)

These help when the user has new results, a new diagnosis, or a new prescription and wants to make sense of it. Modes marked **(no auth)** work without MyChart.

| Command | What it does | Auth? |
|---|---|---|
| `labs` | Lab results (CBC, metabolic, lipid panels, etc.) | Yes |
| `vitals` | Vital signs (BP, HR, weight, temp) | Yes |
| `diagnostics` | Diagnostic reports with conclusions | Yes |
| `drug` | FDA drug info — indications, warnings, dosage, adverse events **(no auth)** | No |
| `icd10` | ICD-10 code lookup by condition or code **(no auth)** | No |
| `interactions` | Drug-drug interaction check via RxNorm **(no auth)** | No |
| `recalls` | FDA drug recall/enforcement actions **(no auth)** | No |

### "Keep Me on Track" (manage ongoing care, medications, conditions)

These help when the user is managing an ongoing condition, tracking medications, or following a care plan.

| Command | What it does | Auth? |
|---|---|---|
| `meds` | Active medications with dosages and prescribers | Yes |
| `conditions` | Active conditions/diagnoses | Yes |
| `allergies` | Allergies and intolerances with severity | Yes |
| `immunizations` | Vaccination history | Yes |
| `careplans` | Active care plans and activities | Yes |
| `goals` | Health goals and achievement status | Yes |
| `appointments` | Upcoming (or past) appointments | Yes |
| `summary` | Full health overview — conditions, meds, labs, vitals, appointments | Yes |

### "Research & Plan" (find providers, compare hospitals, explore trials)

These help when the user is proactively researching options — finding a specialist, comparing hospital quality, or exploring clinical trials. **All work without MyChart auth.**

| Command | What it does |
|---|---|
| `providers` | Search NPI Registry by specialty, condition, location, or name |
| `hospitals` | CMS Hospital Compare — quality ratings, star scores, patient experience |
| `trials` | ClinicalTrials.gov — recruiting trials by condition and location |

### "Deal With the System" (insurance, visit history, documents)

These help when navigating administrative tasks — insurance coverage, billing questions, or accessing clinical documents.

| Command | What it does | Auth? |
|---|---|---|
| `coverage` | Insurance/coverage — payor, plan, subscriber ID, period | Yes |
| `encounters` | Visit/encounter history — type, date, provider, reason | Yes |
| `procedures` | Procedure history with dates and outcomes | Yes |
| `documents` | Clinical documents (filter by type) | Yes |
| `familyhistory` | Family medical history by relationship | Yes |
| `patient` | Demographics — name, DOB, address, contact | Yes |

### Power User

| Command | What it does | Auth? |
|---|---|---|
| `everything` | All patient data via FHIR `$everything` | Yes |
| `lastn` | Latest observation per code (`vital-signs` or `laboratory`) | Yes |
| `search` | Generic FHIR resource search with custom params | Yes |

## First-Run Detection

If the user invoked `/mychart` with **no arguments** or a data mode (not `setup`, `connect`, `orgs`, or any no-auth command), check for first-run:

```bash
python3 -c "
import sys; sys.path.insert(0, '${SKILL_ROOT}/scripts')
from lib.profile_store import get_profile
p = get_profile()
print('onboarding_complete' if p.get('onboarding_complete') else 'needs_onboarding')
"
```

If output is `needs_onboarding` **AND** the user has no connected orgs (see pre-flight below), route to the onboarding wizard: read `${SKILL_ROOT}/references/onboarding.md` and follow those instructions. **Do not continue below.**

## Pre-flight: Check Connection

Before any **auth-required** data mode, verify the user is connected:

```bash
python3 "${SKILL_ROOT}/scripts/auth.py" status
```

If the output shows `"status": "no_orgs"` or all tokens are expired with no refresh:
- Tell the user: "You're not connected to MyChart yet. Let's set that up."
- Route to `references/connect.md`

If tokens are expired but refreshable, the data scripts handle refresh automatically.

**No-auth commands** (`drug`, `icd10`, `interactions`, `providers`, `trials`, `recalls`, `hospitals`): skip the pre-flight check entirely.

## Data Modes (Inline)

All data modes use the same pattern:

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" <mode> [--format compact|json|markdown] [--count N] [--since YYYY-MM-DD] [--active-only]
```

Use a **timeout of 30000** (30 seconds) on the Bash call.

---

### Labs

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" labs --format compact --count 25
```

Synthesize:
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

---

## Clinical Knowledge Tools (No Auth Required)

These tools use public FDA, CMS, and NLM APIs — no MyChart connection needed.

### Drug Lookup

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" drug "metformin"
python3 "${SKILL_ROOT}/scripts/mychart.py" drug "lisinopril" --drug-type event
python3 "${SKILL_ROOT}/scripts/mychart.py" drug "atorvastatin" --drug-type ndc
```

Types: `label` (default — indications, warnings, dosage), `event` (top adverse events), `ndc` (product codes).

### Drug Recalls

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" recalls
python3 "${SKILL_ROOT}/scripts/mychart.py" recalls "metformin"
python3 "${SKILL_ROOT}/scripts/mychart.py" recalls "metformin" --classification "Class I"
```

Searches FDA drug enforcement/recall database. Omit drug name for recent recalls across all drugs. Classification filters: `Class I` (most serious — may cause death or serious harm), `Class II` (may cause temporary/reversible health effects), `Class III` (unlikely to cause harm).

**Synthesis rules:**
- Present recalls clearly: Recall # | Classification | Status | Firm | Reason
- **Highlight Class I recalls prominently** — these are the most serious
- Show the distribution pattern (nationwide vs. regional)
- If the user is connected to MyChart, cross-reference with their active medications via `/mychart meds` and flag any matches
- Include report dates so the user knows how recent the recall is

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

### Provider Finder

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" providers --specialty "Cardiology" --zip-code 90210
python3 "${SKILL_ROOT}/scripts/mychart.py" providers --condition "diabetes,hypertension" --zip-code 90210
python3 "${SKILL_ROOT}/scripts/mychart.py" providers --name "Smith" --city "Los Angeles" --state CA
```

Searches the NPI Registry (public, free, no auth needed). Supports search by specialty, condition (auto-maps to specialty), location, or provider name.

**Synthesis rules:**
- Present providers in a clean table: Name | Specialty | Address | Phone
- **Always note**: NPI Registry does not include insurance network data — providers listed may not accept the user's insurance
- If user has insurance on file (check profile_store), remind them to verify network participation
- For condition-based search: show which conditions mapped to which specialties, and note any unmapped conditions
- If `--org` was used and user is connected, suggest cross-referencing with their conditions via `/mychart conditions`

### Hospital Quality (CMS Hospital Compare)

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" hospitals --state CA --city "Los Angeles"
python3 "${SKILL_ROOT}/scripts/mychart.py" hospitals --name "Mayo"
python3 "${SKILL_ROOT}/scripts/mychart.py" hospitals --zip-code 90210
python3 "${SKILL_ROOT}/scripts/mychart.py" hospitals --provider-id 050454
python3 "${SKILL_ROOT}/scripts/mychart.py" hospitals --provider-id 050454 --detail experience
```

Searches CMS Hospital Compare for hospital info, quality star ratings, and patient experience scores. Data sourced from Medicare — covers virtually all US hospitals.

**Search mode** (no `--provider-id`): returns hospital list with overall star ratings, type, ownership, and emergency services.

**Detail mode** (`--provider-id <id>`): returns domain-specific ratings — mortality, safety, readmission, patient experience, effectiveness, timeliness, efficient imaging. Add `--detail experience` for HCAHPS patient satisfaction survey scores.

**Synthesis rules:**
- Present hospitals in a clean table: Name | Overall Stars | Type | City, State | Phone
- **Star ratings are 1-5** (5 = best). "N/A" means not enough data
- For detail view: show all domain comparisons (Above/Same as/Below National Average)
- For patient experience: summarize top-line satisfaction scores and response rates
- If user has a specific procedure/condition in mind, note which quality domains are most relevant
- Suggest looking at specific hospitals with `--provider-id` for deeper quality data

### Clinical Trials Search

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" trials "type 2 diabetes"
python3 "${SKILL_ROOT}/scripts/mychart.py" trials "type 2 diabetes" --location "California"
python3 "${SKILL_ROOT}/scripts/mychart.py" trials "diabetes,hypertension" --status RECRUITING
python3 "${SKILL_ROOT}/scripts/mychart.py" trials --nct-id NCT12345678
```

Searches ClinicalTrials.gov v2 API (public, free, no auth needed). Comma-separated conditions trigger multi-condition search with deduplication.

**Synthesis rules:**
- Present trials with: Title | Phase | Status | Sponsor | Location(s)
- Show eligibility summary: age range, sex, key inclusion/exclusion criteria
- Include NCT ID for each trial
- For multi-condition search: group results by condition, note any trials that match multiple conditions
- If user is connected to MyChart, suggest cross-referencing with their active conditions
- Note: trial details can be retrieved with `--nct-id` for deeper info on a specific trial

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

Offer context-aware follow-ups based on which mental mode the user is in:

**If interpreting results** (labs, vitals, diagnostics):
- "Want me to look up any of these values, check your medications, or show trends?"
- If abnormal results found: "Want me to check if any of your current medications could affect these values?" (offer `interactions`)

**If managing ongoing care** (meds, conditions, careplans, summary):
- "Want me to check for drug interactions, look up any of these medications, or check for recalls?"
- If medications shown: "Want me to check if any of these have active FDA recalls?" (offer `recalls`)

**If researching options** (providers, hospitals, trials):
- "Want me to get detailed quality ratings for any of these hospitals, or search for clinical trials?"
- If providers shown: "Want me to compare hospital quality in your area?" (offer `hospitals`)

**If navigating the system** (coverage, encounters, documents):
- "Want me to show your upcoming appointments, or pull up a specific document?"

Stay in expert mode for the conversation — don't re-fetch data unless the user asks for a different mode or a refresh.
