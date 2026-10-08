![banner](banner.png)

# venue-booking-audit-skill

![repo](https://img.shields.io/badge/仓库-公开-brightgreen)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![platform](https://img.shields.io/badge/平台-师悦未来校园-green)
![type](https://img.shields.io/badge/类型-agent%20skill-purple)

> 针对**师悦平台**（未来校园 · 场馆预约模块）的场馆预约审核 skill，供 agent 复用。

📖 English: [README.md](README.md)

## 这个 skill 做什么

把一个人的审核工作流固化成可复用的 skill：

1. **查** —— 列出你管辖场馆的待审核预约（`status=2`）。
2. **摆** —— 展示申请人、场馆、日期、时段、人数、备注、提交时间，然后停下来等。
3. **定** —— 每条都必须由人当次亲口说"通过"或"驳回"，绝不自动审批。
4. **执行** —— 调审核接口（`auditStatus=3` 通过 / `4` 驳回）。
5. **同步** —— 通过的预约记进 iCloud「工作」日历（写入时按名称实时查找，不硬编码 ID）。

## 需要你提供什么

| # | 事项 | 放在哪里 | 说明 |
|---|------|----------|------|
| 1 | **师悦平台账号密码** | `~/hooks/state/cg_creds`，两行：`CM_USER=<用户名>`、`CM_PASS=<密码>`，文件权限 `600` | 只用于登录，绝不打印、不记日志、不提交。改密码后记得更新这个文件，否则登录失败。 |
| 2 | **平台网址 / IP** | `bin/cg_audit.py` 里的 `BASE`（或环境变量 `CG_BASE_URL`） | 你学校的师悦平台地址——公开仓库里不要写真实内网 IP。 |
| 3 | **管辖的场馆类型 ID** | `bin/cg_audit.py` 里的 `MANAGED_VENUE_TYPE_IDS` | 默认 `13` 实验室、`15` 声乐教室、`17` 大礼堂。按你实际审核的场馆调整。 |
| 4 | **iCloud 日历** | 写入时按名称实时查找 | 通过的预约只进名叫「工作」的日历，不写其他任何日历。 |
| 5 | **配对的 iPhone（已授权日历）** | 通过 agent 的设备工具调用 | 审核通过后用来建日历事件。 |

Python 依赖：`requests`、`cryptography`
（缺失时执行 `python3 -m pip install --break-system-packages requests cryptography`；
注意 VM 重装会清空系统包，import 报错时重装即可。）

## 快速上手

```bash
# 1. 写凭证（权限 600，这个文件绝不提交）
printf 'CM_USER=<用户名>\nCM_PASS=<密码>\n' > ~/hooks/state/cg_creds
chmod 600 ~/hooks/state/cg_creds

# 2. 装依赖
python3 -m pip install --break-system-packages requests cryptography

# 3. 冒烟测试（只读）
python3 bin/cg_audit.py list
```

## 给 agent 的用法

```
python3 bin/cg_audit.py list                 # 列出管辖场馆的待审核
python3 bin/cg_audit.py approve <bookingId>  # 通过（auditStatus=3）
python3 bin/cg_audit.py reject <bookingId>   # 驳回（auditStatus=4）
```

完整操作规范见 [SKILL.md](SKILL.md)；接口细节见 [references/api.md](references/api.md)。

## 安全红线

- **绝不自动通过 / 自动驳回**，每条都要当次人工明确决定。
- 一句"通过"只对应刚才摆出来的那一条；多条待审时先确认是哪条再执行。
- 通过 → 只进 iCloud「工作」日历；驳回 → 不建日历。
- 账号密码绝不打印、不记日志、不提交。

## 目录结构

```
├── SKILL.md            # 给 agent 的操作规范
├── README.md           # English docs
├── README.zh-CN.md     # 本文件
├── banner.png   # README 头图
├── bin/cg_audit.py     # list / approve / reject 工具
└── references/api.md   # 师悦平台接口参考
```
