#!/usr/bin/env python3
"""未来校园场馆预约审核 helper（venue-booking-audit skill 用）.

用法:
    cg_audit.py list                    # 列出待审核预约（status=2，管辖场馆）
    cg_audit.py approve <bookingId>     # 通过（auditStatus=3）
    cg_audit.py reject <bookingId>      # 驳回（auditStatus=4）

凭证读 ~/hooks/state/cg_creds（600 权限），绝不打印。
重要：approve/reject 只在用户当次明确说"通过"/"驳回"后调用，绝不自动执行。
"""
import os
import sys
import base64
import time
import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

# 填你学校的师悦平台地址；也可通过环境变量 CG_BASE_URL 覆盖
BASE = os.environ.get("CG_BASE_URL", "http://<your-shiyue-host>:<port>")
STATE_DIR = os.path.join(os.path.expanduser("~"), "hooks", "state")
MANAGED_VENUE_TYPE_IDS = {13, 15, 17}  # 实验室, 声乐教室, 大礼堂


def load_creds():
    creds = {}
    with open(os.path.join(STATE_DIR, "cg_creds")) as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip()
    return creds["CM_USER"], creds["CM_PASS"]


def login(user, pwd):
    s = requests.Session()
    ret = Retry(total=4, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
    s.mount("http://", HTTPAdapter(max_retries=ret))
    s.headers.update({"User-Agent": "Mozilla/5.0", "Origin": BASE, "Referer": BASE + "/"})
    d = s.get(BASE + "/api/uaa/oauth/public_key", timeout=20).json()["data"]
    pub = serialization.load_der_public_key(base64.b64decode(d.replace("\r", "").replace("\n", "")))
    eu = base64.b64encode(pub.encrypt(user.encode(), padding.PKCS1v15())).decode()
    ep = base64.b64encode(pub.encrypt(pwd.encode(), padding.PKCS1v15())).decode()
    sig = "SYSN_" + str(int(time.time() * 1000))
    r = s.post(BASE + "/api/uaa/oauth/login_key",
               data={"username": eu, "password": ep, "signature": sig}, timeout=25)
    j = r.json()
    if j.get("code") != "ok" or not (j.get("data") or {}).get("authenticated"):
        raise RuntimeError("login failed: " + r.text[:200])
    info = j["data"]
    s.headers.update({"Authorization": "Bearer " + info["accessToken"]})
    return s, info


def pending_bookings(s, unit_id):
    r = s.get(BASE + "/api/cg/select/booking",
              params={"start": 1, "size": 50, "unitId": unit_id, "status": 2}, timeout=25)
    j = r.json()
    if j.get("code") != "ok":
        raise RuntimeError("booking query failed: " + r.text[:200])
    items = (j.get("data") or {}).get("list") or []
    out = []
    for it in items:
        if it.get("status") != 2 and str(it.get("status")) != "2":
            continue
        vt = it.get("venueTypeId")
        try:
            vt = int(vt)
        except (TypeError, ValueError):
            vt = None
        if vt not in MANAGED_VENUE_TYPE_IDS:
            continue
        out.append({
            "id": it.get("id"),
            "venueName": it.get("venueName"),
            "venueTypeName": it.get("venueTypeName"),
            "applicant": it.get("useUserName") or it.get("creatorName"),
            "date": (it.get("bookingEnd") or "")[:10],
            "timeRange": it.get("sectionName"),
            "persons": it.get("persons"),
            "remark": it.get("useRemark") or it.get("remark"),
            "createdDate": it.get("createdDate"),
        })
    return out


def audit(s, booking_id, approve):
    r = s.post(BASE + "/api/cg/manage/booking/audit",
               data={"bookingId": booking_id,
                     "auditStatus": 3 if approve else 4}, timeout=25)
    j = r.json()
    if r.status_code != 200 or j.get("code") != "ok":
        raise RuntimeError("audit failed: " + r.text[:300])
    return j


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("list", "approve", "reject"):
        print(__doc__)
        sys.exit(2)
    user, pwd = load_creds()
    s, info = login(user, pwd)
    cmd = sys.argv[1]
    if cmd == "list":
        print(json.dumps(pending_bookings(s, info["unitId"]), ensure_ascii=False, indent=2))
    else:
        if len(sys.argv) < 3:
            print("need bookingId", file=sys.stderr)
            sys.exit(2)
        j = audit(s, sys.argv[2], approve=(cmd == "approve"))
        print(json.dumps({"ok": True, "decision": cmd,
                          "bookingId": sys.argv[2]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
