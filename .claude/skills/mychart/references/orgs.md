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

If user wants to remove an org:

1. First show them their orgs (use the status command above) so they can confirm which one to remove
2. Get the org_id from the status output
3. Confirm with the user before removing — this deletes all stored tokens for that org
4. Run:

```bash
python3 -c "
import sys; sys.path.insert(0, '${SKILL_ROOT}/scripts')
from lib.token_store import remove_org
removed = remove_org(ORG_ID)
print('removed' if removed else 'not_found')
"
```

Replace `ORG_ID` with the actual integer org ID.

If the removed org was the default, suggest setting a new default by reconnecting to another org.

### Switch Default

If user wants to switch their default org:

```bash
python3 -c "
import sys; sys.path.insert(0, '${SKILL_ROOT}/scripts')
from lib.token_store import set_default_org
success = set_default_org(ORG_ID)
print('default_set' if success else 'not_found')
"
```

Replace `ORG_ID` with the actual integer org ID from the status listing.

### Token Issues

If a token is expired:
- If refreshable: suggest `/mychart connect "Org Name"` to re-authenticate
- If not refreshable: same — must re-authenticate
