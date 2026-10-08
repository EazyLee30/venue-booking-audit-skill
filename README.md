![banner](banner.png)

# venue-booking-audit-skill

![repo](https://img.shields.io/badge/repo-public-brightgreen)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![platform](https://img.shields.io/badge/platform-%E5%B8%88%E6%82%A6%E6%9C%AA%E6%9D%A5%E6%A0%A1%E5%9B%AD-green)
![type](https://img.shields.io/badge/type-agent%20skill-purple)

> Reusable agent skill for auditing venue bookings on the **Shiyue （师悦） campus platform** （未来校园 · 场馆预约 module).

📖 中文文档：[README.zh-CN.md](README.zh-CN.md)

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
├── README.md           # this file (English)
├── README.zh-CN.md     # 中文文档
├── banner.png   # README banner
├── bin/cg_audit.py     # list / approve / reject helper
└── references/api.md   # Shiyue platform API reference
```
