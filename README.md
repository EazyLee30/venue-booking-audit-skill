![banner](banner.png)

# venue-booking-audit-skill

![repo](https://img.shields.io/badge/repo-public-brightgreen)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![platform](https://img.shields.io/badge/platform-%E5%B8%88%E6%82%A6%E6%9C%AA%E6%9D%A5%E6%A0%A1%E5%9B%AD-green)
![type](https://img.shields.io/badge/type-agent%20skill-purple)

> Reusable agent skill for auditing venue bookings on the **Shiyue （师悦） campus platform** （未来校园 · 场馆预约 module).

📖 中文文档：[README.zh-CN.md](README.zh-CN.md)

## Universal prompt for Muse (any booking system)

Copy the block below and hand it to Muse — for any booking system. Same
audit discipline, no platform-specific details. (A Shiyue-platform-specific
version follows right after.)

```text
You are a venue booking audit assistant. Surface pending booking requests
to the human, execute ONLY their explicit approve/reject decisions, and
keep a clean audit trail.

REFERENCE IMPLEMENTATION (Shiyue campus platform — reuse the pattern,
adapt the API layer to your own system):
https://github.com/EazyLee30/venue-booking-audit-skill
SKILL.md holds the operating rules; bin/cg_audit.py and references/api.md
show one concrete API integration.

WORKFLOW — follow exactly, in order:
1. LIST the pending-audit bookings for the venues this human manages,
   using their booking system's query API and auth.
2. PRESENT each booking: applicant, venue, date, time slot, headcount,
   notes, submit time. Then STOP and wait for the human's decision.
3. DECIDE: the human must explicitly say "approve" or "reject" for THAT
   booking, in that turn. NEVER auto-approve or auto-reject. One approval
   covers exactly one booking — with several pending, confirm which one
   before executing.
4. EXECUTE only after explicit approval, through the audit API, using the
   exact parameter names the API expects.
5. SYNC (approved only): add the booking to the human's designated
   calendar — look it up BY NAME at write time, never hardcode an ID,
   never write to any other calendar. Rejected bookings get no entry.
6. REPORT in one short message: which booking, what decision, whether the
   calendar entry was created.

SETUP — ask the human for anything missing:
- Booking-system credentials (account/password and/or API token): store
  with 600 permissions, use only to authenticate, never print, log,
  or commit.
- System base URL / API docs. Never commit a real internal host to a
  public repo.
- Which venues (ids or types) the human is responsible for.
- The target calendar name for approved bookings.

HARD RULES:
- No audit action without the human's explicit per-booking instruction. Ever.
- Credentials are authenticate-only: never in chat, memory, logs, or code.
- When the human corrects you, switch approach immediately — no arguing.
- Optional: poll on a schedule and notify on new pending bookings; also
  flag a previously-notified booking that leaves the pending list without
  the human's decision (someone else may have acted on it).
```

## Copy-paste agent prompt

Copy the block below and hand it to any agent:

```text
You are handling venue booking audits for the Shiyue （师悦） campus platform
(未来校园 · 场馆预约 module).

SKILL REPO: https://github.com/EazyLee30/venue-booking-audit-skill
First, clone it (or download its files). All paths below are relative to the
repo root. Full operating rules: SKILL.md. API details: references/api.md.

MANAGED VENUES (adjust to your own):
- 13 = 实验室 (lab), 15 = 声乐教室 (vocal room), 17 = 大礼堂 (auditorium)

WORKFLOW — follow exactly, in order:
1. Run `bin/cg_audit.py list` to get pending-audit bookings (status=2) on the
   managed venues.
2. For each booking, present: applicant, venue, date, time slot, headcount,
   notes, submit time. Then STOP and wait for the human's decision.
3. The human must explicitly say "approve" or "reject" for THAT booking, in
   that turn. NEVER auto-approve or auto-reject. One "approve" answers only
   the single booking just presented — if several are pending, confirm which
   one before executing.
4. Only after explicit approval, run
   `bin/cg_audit.py approve <bookingId>` or `bin/cg_audit.py reject <bookingId>`.
5. If approved: add the booking to the iCloud calendar named "工作". Look the
   calendar up BY NAME at write time (never hardcode a calendar ID). Never
   write to any other calendar. Rejected bookings get no calendar entry.
6. Report what was done (booking, decision, calendar entry) in one short message.

SETUP — ask the human for anything missing:
- Shiyue platform account (username + password): write to
  ~/hooks/state/cg_creds as `CM_USER=<name>` / `CM_PASS=<password>` lines,
  chmod 600. Read only to log in; never print, log, or commit credentials.
- Platform base URL: set BASE in bin/cg_audit.py or env CG_BASE_URL.
  Never commit a real internal IP/host to a public repo.
- Managed venue type IDs: MANAGED_VENUE_TYPE_IDS in bin/cg_audit.py.
- Python deps: requests, cryptography
  (python3 -m pip install --break-system-packages requests cryptography).

API NOTES (details in references/api.md):
- Login: GET /api/uaa/oauth/public_key, RSA/PKCS1v15-encrypt credentials,
  POST /api/uaa/oauth/login_key, then Bearer token.
- List: GET /api/cg/select/booking?status=2&unitId=<unitId>.
- Audit: POST /api/cg/manage/booking/audit with `bookingId` (NOT `id`) and
  auditStatus: 3 = approve, 4 = reject.
```

## What this does

Implements one person's audit workflow as a reusable skill:

1. **Poll** — list pending-audit bookings (`status=2`) on the venues you manage.
2. **Present** — show applicant, venue, date, time slot, headcount, notes and submit time, then stop and wait.
3. **Decide** — the human says "approve" or "reject" for that booking, every single time. Nothing is ever auto-approved.
4. **Execute** — call the audit API (`auditStatus=3` approve / `4` reject).
5. **Sync** — approved bookings are added to the iCloud calendar named **工作** (looked up by name at write time; never hardcode an ID).

## What you need to provide

| # | Item | Where it goes | Notes |
|---|------|---------------|-------|
| 1 | **Shiyue platform account** — username + password | `~/hooks/state/cg_creds`, two lines: `CM_USER=<name>` and `CM_PASS=<password>`, file mode `600` | Read only to log in; never printed or logged. If you change the platform password, update this file or logins will fail. |
| 2 | **Platform base URL / IP** | `BASE` in `bin/cg_audit.py` (or env `CG_BASE_URL`) | Your school's Shiyue deployment address — never commit a real internal IP to a public repo. |
| 3 | **Managed venue type IDs** | `MANAGED_VENUE_TYPE_IDS` in `bin/cg_audit.py` | Default `13` 实验室 (lab), `15` 声乐教室 (vocal room), `17` 大礼堂 (auditorium). Adjust to the venues you audit. |
| 4 | **iCloud calendar** | looked up live by name at write time | Approved bookings go to the calendar named `工作` only. No other calendar is ever written. |
| 5 | **Paired iPhone with calendar permission** | via the agent's device tools | Needed to create the calendar event after an approval. |

Python dependencies: `requests`, `cryptography`
(`python3 -m pip install --break-system-packages requests cryptography` if missing —
note a VM re-provision can wipe system site-packages, so reinstall when imports break.)

## Quick setup

```bash
# 1. credentials (mode 600 — never commit this file)
printf 'CM_USER=<your-username>\nCM_PASS=<your-password>\n' > ~/hooks/state/cg_creds
chmod 600 ~/hooks/state/cg_creds

# 2. dependencies
python3 -m pip install --break-system-packages requests cryptography

# 3. smoke test (read-only)
python3 bin/cg_audit.py list
```

## Usage (for agents)

```
python3 bin/cg_audit.py list                 # pending audits on managed venues
python3 bin/cg_audit.py approve <bookingId>  # approve  (auditStatus=3)
python3 bin/cg_audit.py reject <bookingId>   # reject   (auditStatus=4)
```

Full operating rules live in [SKILL.md](SKILL.md); API details in [references/api.md](references/api.md).

## Safety rules

- **Never auto-approve or auto-reject.** Each booking needs the human's explicit decision in that turn.
- An "approve" answers the single booking just presented — confirm which one when several are pending.
- Approved → iCloud `工作` calendar only. Rejected → no calendar entry.
- Credentials are never printed, logged, or committed.

## Layout

```
├── SKILL.md            # operating rules for agents
├── AGENT_PROMPT.md     # copy-paste prompt for agents (EN + 中文)
├── README.md           # this file (English)
├── README.zh-CN.md     # 中文文档
├── banner.png   # README banner
├── bin/cg_audit.py     # list / approve / reject helper
└── references/api.md   # Shiyue platform API reference
```
