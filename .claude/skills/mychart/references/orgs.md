# MyChart Organizations — Management Instructions

## Instructions for Claude

When the user runs `/mychart orgs`, manage their connected organizations.

### List Organizations

```bash
python3 "${SKILL_ROOT}/scripts/auth.py" status
```

Parse the JSON output and display a clean summary:

```
Connected Organizations:
├─ ★ Kaiser Permanente (default)
│    Patient: abc123 | Token: valid until 2026-03-24 14:30
│    Scopes: patient/*.read openid fhirUser
├─ Mayo Clinic
│    Patient: def456 | Token: expired (refreshable)
└─ Epic Sandbox (Test)
     Patient: test123 | Token: valid until 2026-03-24 15:00
```

### Switch Default

If user says "switch to Mayo Clinic" or "use Mayo":
- Look up the org_id from the status output
- The skill currently handles this via the connect flow (reconnecting sets default)
- Tell the user to run: `/mychart connect "Mayo Clinic"` to switch

### Remove Organization

If user wants to remove an org, note that this requires direct DB modification.
For now, tell the user:
> Organization removal will be available in a future update. For now, you can connect to a different org to change your default.

### Token Issues

If a token is expired:
- If refreshable: suggest `/mychart connect "Org Name"` to re-authenticate
- If not refreshable: same — must re-authenticate
