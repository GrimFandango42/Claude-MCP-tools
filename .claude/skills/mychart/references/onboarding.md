# MyChart Onboarding Wizard

## Instructions for Claude

This wizard runs when the user invokes `/mychart setup` or on first-run detection (no orgs in DB and no onboarding_complete flag). Guide the user through 5 steps using the canvas card format functions below.

**Key principles:**
- Value before credentials — lead with clinical tools that need no auth
- Hide the plumbing — never say "PKCE", "FHIR", "OAuth" to the user
- Progressive disclosure — don't overwhelm, reveal step by step
- Escape hatches — every step can be skipped
- Contextual bridges — each step naturally leads to the next

---

## Step 0: Detect First Run

```bash
python3 "${SKILL_ROOT}/scripts/auth.py" status 2>/dev/null
```

```bash
python3 -c "
import sys; sys.path.insert(0, '${SKILL_ROOT}/scripts')
from lib.profile_store import get_profile
p = get_profile()
print('onboarding_complete' if p.get('onboarding_complete') else 'needs_onboarding')
"
```

- If `status` shows connected orgs AND profile has `onboarding_complete`: **skip wizard**, proceed normally.
- If user explicitly ran `/mychart setup`: **always run wizard** (allows re-running).
- Otherwise: **start wizard at Step 1**.

---

## Step 1: Welcome & Capability Overview

Present the welcome card to the user. Use this exact markdown canvas format:

```markdown
### Welcome to MyChart

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

**Optional extras:**
- Scan your insurance card for quick reference
- Save your health profile for personalized experience

---
**What would you like to do?**
1. Try a drug lookup right now (no sign-in needed)
2. Connect my health system
3. Just exploring — tell me more
```

Use `AskUserQuestion` to get their choice.

**Routing:**
- Choice 1 → Go to **Step 2** (Try Before Sign-In)
- Choice 2 → Go to **Step 3** (Connect Health System)
- Choice 3 → Briefly explain each capability category, then ask again

---

## Step 2: Try Before You Sign In

**Goal:** Deliver instant value. Build trust before asking for credentials.

Prompt the user:
> Want to try a quick drug lookup? Name any medication — something you take, or anything you're curious about.

Wait for their response with `AskUserQuestion`.

When they name a drug, run:

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" drug "[DRUG_NAME]" --format compact
```

Present the results as a formatted drug card:

```markdown
### [Drug Name]

| Field | Details |
|-------|---------|
| Brand Names | [from results] |
| Drug Class | [from results] |
| Route | [from results] |
| **Indications** | [from results] |
| **Key Warnings** | [top 2-3 warnings] |

> **Tip:** You can also check interactions between medications — just name 2 or more drugs.
>
> Ready to see your actual medication list? Let's connect your health system.
```

Then ask:
> Would you like to:
> 1. Check interactions between medications
> 2. Connect your health system now
> 3. Skip to a different step

- Choice 1 → Ask for 2+ drug names, run `interactions`, then re-offer connect
- Choice 2 → Go to **Step 3**
- Choice 3 → Ask what they'd like to do

---

## Step 3: Connect Your Health System

**Goal:** Make authentication feel simple and safe.

### 3a: Choose Provider

Present the provider picker:

```markdown
### Connect Your Health System

**Popular systems:**

| # | Health System |
|---|--------------|
| 1 | Kaiser Permanente |
| 2 | Mayo Clinic |
| 3 | Cleveland Clinic |
| 4 | Johns Hopkins |
| 5 | Mount Sinai |
| 6 | Cedars-Sinai |
| 7 | Mass General Brigham |
| 8 | UCSF Health |
| 9 | Duke Health |
| 10 | NYU Langone |

**Or type your health system name** — most Epic MyChart systems are supported.

> *Want to test with fake data first? Type "sandbox"*
```

Use `AskUserQuestion` to get their choice.

### 3b: PHI Acknowledgment

**CRITICAL** — Before auth, always show:

```markdown
### Before We Connect

> **Privacy Notice:** Connecting will allow me to access your health records
> (lab results, medications, conditions, etc.) to help answer your questions.
>
> - Your health data is processed **during this conversation only**
> - Health data is **NOT stored** on disk — only login tokens are saved locally
> - You can disconnect at any time
>
> **Do you want to proceed?**
```

Wait for explicit confirmation via `AskUserQuestion`. Do NOT proceed without it.

### 3c: Run Authentication

Show progress:

```markdown
### Connecting to [Health System]...

- [x] Found [Health System] endpoint
- [x] Security handshake prepared
- [ ] Waiting for you to sign in via browser...

A browser window should have opened. Sign in with your MyChart username and password.

> *Browser didn't open? Let me know and I'll give you a direct link.*
```

Run the auth script:

```bash
python3 "${SKILL_ROOT}/scripts/auth.py" connect "[ORG_NAME]"
```

For sandbox:
```bash
python3 "${SKILL_ROOT}/scripts/auth.py" connect --sandbox
```

**If sandbox**, also tell the user:
> Sign in with test credentials: **username** `fhirderrick` / **password** `epicepic1`

Parse the JSON output:

- `"awaiting_auth"` with `mode: "localhost"` → Tell user to complete browser sign-in. Wait for the callback.
- `"awaiting_auth"` with `mode: "manual"` → Share the `auth_url`, ask user to paste code back.
- `"connected"` → Show success card (3d).
- `"error"` → Show error, offer to retry or skip.

### 3d: Connection Success

```markdown
### Connected!

| Detail | Value |
|--------|-------|
| Health System | [org name] |
| Patient ID | [patient_id] |
| Session expires | [expiry time] |
| Available data | [count of scopes] categories |

**What's next?**
1. Add your insurance card (optional, 1 minute)
2. See your health snapshot now
3. Skip ahead — I'll explore on my own
```

Use `AskUserQuestion` for routing:
- Choice 1 → **Step 4** (Insurance)
- Choice 2 → **Step 5** (Health Snapshot)
- Choice 3 → Mark onboarding complete, exit wizard

---

## Step 4: Insurance Card (Optional)

**Goal:** Capture insurance info while the user is in setup mode.

```markdown
### Insurance Card (Optional)

Save your insurance details for quick reference.

**How would you like to add it?**
1. Upload/paste a photo of your card
2. Type or paste the info from your card
3. Skip — I'll do this later
```

Use `AskUserQuestion`.

### 4a: Image Upload

If user provides an image path or pastes an image:

```python
python3 -c "
import sys; sys.path.insert(0, '${SKILL_ROOT}/scripts')
from lib.insurance import parse_insurance_image_prompt
print(parse_insurance_image_prompt('[IMAGE_PATH]'))
"
```

Use the returned prompt to analyze the image with your vision capabilities, then extract the fields.

### 4b: Text Input

If user types/pastes text from their card:

```bash
python3 -c "
import sys, json; sys.path.insert(0, '${SKILL_ROOT}/scripts')
from lib.insurance import parse_insurance_text
result = parse_insurance_text('''[USER_TEXT]''')
print(json.dumps(result, indent=2))
"
```

### 4c: Review & Confirm

Present the parsed results for confirmation:

```markdown
### Insurance Card — Review

| Field | Parsed Value | Confidence |
|-------|-------------|------------|
| Insurance Company | [payor] | [confidence] |
| Plan Type | [plan_type] | [confidence] |
| Member ID | [member_id] | [confidence] |
| Group # | [group_number] | [confidence] |
| Phone | [phone] | [confidence] |
| Rx BIN | [rx_bin] | [confidence] |
| Rx PCN | [rx_pcn] | [confidence] |

**Does this look right?**
1. Yes — save it
2. I need to fix something
3. Discard — don't save
```

If saving:

```bash
python3 -c "
import sys; sys.path.insert(0, '${SKILL_ROOT}/scripts')
from lib.profile_store import save_insurance
plan_id = save_insurance(
    plan_name='[plan_name]',
    payor='[payor]',
    member_id='[member_id]',
    group_number='[group_number]',
    plan_type='[plan_type]',
    phone='[phone]'
)
print(f'Saved as plan #{plan_id}')
"
```

If fixing: ask which fields to correct, update, then re-confirm.

Then proceed to **Step 5**.

---

## Step 5: Health Snapshot

**Goal:** The payoff — show the user their own data.

This is the "aha moment." Fetch a summary and present it as a dashboard.

```bash
python3 "${SKILL_ROOT}/scripts/mychart.py" summary --format compact
```

Use a **30-second timeout** on this call.

Present results as a health dashboard:

```markdown
### Your Health Snapshot — [Month Year]

---

**Active Conditions**
[List each condition with onset date]

---

**Current Medications** ([count])
| Medication | Dosage | Frequency |
|-----------|--------|-----------|
| [drug] | [dose] | [frequency] |

---

**Recent Labs** (last 90 days)
| Test | Value | Range | Status |
|------|-------|-------|--------|
| [test] | [value] | [range] | [flag: normal/high/low] |

---

**Recent Vitals**
| Vital | Reading | Date |
|-------|---------|------|
| [type] | [value] | [date] |

---

**Allergies**
[List with severity]

---

**Upcoming Appointments**
| Date | Provider | Type |
|------|----------|------|
| [date] | [provider] | [type] |

---

> **Dive deeper:** `labs` · `meds` · `vitals` · `conditions` · `appointments` · `summary`
>
> Ask me anything about your health data.
```

**CRITICAL output rules (same as main skill):**
- Use exact values from FHIR data — do NOT approximate or round
- Always show units (mg/dL, mmHg, etc.)
- Flag abnormal results clearly
- Do NOT make clinical recommendations or diagnoses
- Suggest discussing concerns with healthcare provider

---

## Step 6: Complete Onboarding

After Step 5 (or if user skips to exit at any point), mark onboarding complete:

```bash
python3 -c "
import sys; sys.path.insert(0, '${SKILL_ROOT}/scripts')
from lib.profile_store import save_profile
save_profile(onboarding_complete=True)
print('Onboarding complete')
"
```

Then tell the user:

```markdown
### You're all set!

Here's a quick reference for what you can do:

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
| `/mychart interactions [drug1] [drug2]` | Check drug interactions |
| `/mychart icd10 [term]` | Look up diagnosis codes |
| `/mychart connect [org]` | Add another health system |
| `/mychart setup` | Re-run this wizard |

Just ask — I can pull up any of your health data anytime.
```

---

## Error Recovery During Wizard

| Error | Recovery |
|-------|----------|
| Auth fails | Offer retry or skip: "We can set this up later. Want to try the clinical tools instead?" |
| Insurance parse low confidence | Show results anyway with warnings, let user correct manually |
| Summary fetch fails | Try individual modes (labs, meds) as fallback. Show whatever data is available. |
| Network issues | "Having trouble reaching the server. Want to try again, or explore the offline tools (drug lookup, ICD-10)?" |
| User wants to quit mid-wizard | Always allow. Mark onboarding_complete if they connected successfully. |

## Re-Running the Wizard

If user runs `/mychart setup` again:
- Skip Step 0 detection, always run
- At Step 1, note any existing connections: "You're already connected to [org]. Want to add another system or re-do your setup?"
- At Step 4, show existing insurance if any: "You have [plan] on file. Want to update it or add another?"
