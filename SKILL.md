---
name: "venue-booking-audit"
description: "Audit workflow for the 未来校园 venue booking system: list pending approvals, present full details for the user's decision, execute approve/reject via API only on explicit approval, and add approved bookings to the iCloud 工作 calendar."
metadata: { "includeInPrompt": true }
---

# Venue Booking Audit

## Purpose
Handle venue booking audits the way 李奕志 does: he manages 实验室, 声乐教室 and 大礼堂. New pending bookings surface with full details, he decides approve/reject each time, the decision is executed via API, and approved bookings go to the iCloud "工作" calendar. Use this whenever a booking needs auditing, or when setting up the monitoring loop for another agent.

## Workflow
1. **List pending**: run `bin/cg_audit.py list` to get bookings with `status=2` on the managed venues.
2. **Present for decision**: show 申请人, 场馆, 日期, 时段, 使用人数, 备注, 提交时间. Then STOP and wait. The user must say "通过" or "驳回" for that specific booking, in that turn.
3. **Execute**: only after explicit approval, run `bin/cg_audit.py approve <bookingId>` or `bin/cg_audit.py reject <bookingId>`.
4. **Calendar (approve only)**: add the booking to the iCloud calendar named "工作". Look the calendar up by name at write time (names can change; never hardcode an ID). Never write to any other calendar.

## Tooling
`bin/cg_audit.py` — self-contained helper (login + list/approve/reject):
```
bin/cg_audit.py list                      # pending audits on managed venues
bin/cg_audit.py approve <bookingId>        # auditStatus=3
bin/cg_audit.py reject <bookingId>         # auditStatus=4
```
Needs `cryptography` and `requests` on the Python that runs it. If the host VM re-provisions and the import breaks, reinstall: `python3 -m pip install --break-system-packages cryptography requests`.

## Auth
Credentials live at `~/hooks/state/cg_creds` (mode 600, `CM_USER`/`CM_PASS` lines). Read them only to log in; never print, log, or repeat them. If the user changes the 未来校园 password, the login breaks — tell the user to re-provide credentials, do not attempt to recover them yourself.

## Operating Rules
1. **Never auto-approve or auto-reject.** No batch approvals, no "probably fine". Each booking needs the user's explicit decision in that turn.
2. A "通过" answers the single booking just presented. If several are pending, confirm which one before executing.
3. Approved bookings go to the iCloud "工作" calendar only. Rejected bookings get no calendar entry.
4. Look up the "工作" calendar by name at write time; do not reuse a stored calendar ID.
5. After executing, report what was done (booking, decision, calendar entry) in one short message.
6. API details (endpoints, login crypto, params) live in `references/api.md`.
