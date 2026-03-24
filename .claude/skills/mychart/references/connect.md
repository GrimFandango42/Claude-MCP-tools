# MyChart Connect — OAuth2 Setup Flow

## Instructions for Claude

When the user runs `/mychart connect`, follow this flow:

### 1. Determine Target Organization

Ask the user which health system to connect to if not specified:
- If they said `connect --sandbox` → use Epic sandbox (no registration needed)
- If they named an org → pass it to the script
- If unclear → ask: "Which health system do you want to connect to? (e.g., 'Kaiser Permanente', 'Mayo Clinic', or use --sandbox to test)"

### 2. PHI Acknowledgment

**CRITICAL**: Before starting auth, inform the user:

> **Important**: Connecting MyChart will allow me to access your health records (lab results, medications, conditions, etc.) to answer your questions. Your health data will be processed during our conversation but is NOT stored permanently by this skill. Only your OAuth tokens are saved locally.
>
> Do you want to proceed?

Wait for confirmation before continuing.

### 3. Run Auth Script

```bash
python3 "${SKILL_ROOT}/scripts/auth.py" connect [ORG_NAME] [--sandbox] [--manual]
```

The script outputs JSON. Parse the `status` field:

- `"awaiting_auth"` → The script needs user interaction:
  - If `mode` is `"localhost"`: Tell the user a browser window should open. If it doesn't, share the `auth_url` for them to open manually. The script will handle the callback automatically.
  - If `mode` is `"manual"`: Share the `auth_url` and tell the user to sign in, then paste the authorization code back.

- `"connected"` → Success! Display:
  ```
  Connected to {org}!
  Patient ID: {patient_id}
  Scopes: {scopes}

  You can now use:
  - /mychart labs — recent lab results
  - /mychart meds — current medications
  - /mychart conditions — active diagnoses
  - /mychart allergies — allergy list
  - /mychart vitals — recent vital signs
  - /mychart summary — comprehensive health overview
  ```

- `"error"` → Display the error message and suggest fixes.

### 4. Sandbox Testing

For `--sandbox`, inform the user:
> Using Epic's test sandbox. Sign in with these test credentials:
> - Username: `fhirderrick`
> - Password: `epicepic1`
>
> This uses synthetic test data, not real patient records.

### 5. Error Recovery

| Error | Fix |
|---|---|
| "No client_id available" | User needs to set `EPIC_CLIENT_ID` env var or use `--sandbox` |
| "Could not discover OAuth endpoints" | FHIR URL may be wrong. Check at open.epic.com/MyApps/Endpoints |
| "Token exchange failed" | Auth code may have expired. Try again. |
| "State mismatch" | Possible CSRF. Start over with a fresh connect. |
