![banner](banner.png)

# venue-booking-audit-skill

![repo](https://img.shields.io/badge/仓库-公开-brightgreen)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![platform](https://img.shields.io/badge/平台-师悦未来校园-green)
![type](https://img.shields.io/badge/类型-agent%20skill-purple)

> 针对**师悦平台**（未来校园 · 场馆预约模块）的场馆预约审核 skill，供 agent 复用。

📖 English: [README.md](README.md)

## 直接复制给 agent 的 prompt

复制下面的代码块，丢给任何 agent 即用：

```text
你要负责师悦平台（未来校园 · 场馆预约模块）的场馆预约审核。

SKILL 仓库：https://github.com/EazyLee30/venue-booking-audit-skill
先把它 clone 下来（或下载里面的文件）。下面所有路径都是相对仓库根目录的。
完整操作规范见 SKILL.md，接口细节见 references/api.md。

管辖场馆（按你自己的调整）：
- 13 = 实验室，15 = 声乐教室，17 = 大礼堂

工作流——严格按顺序执行：
1. 运行 `bin/cg_audit.py list`，列出管辖场馆的待审核预约（status=2）。
2. 每条预约摆出：申请人、场馆、日期、时段、人数、备注、提交时间，然后停下来等人的决定。
3. 每条都必须由人当次亲口说"通过"或"驳回"，绝不自动审批。一句"通过"只对应刚才摆出来的那一条；多条待审时先确认是哪条再执行。
4. 只有拿到明确批准后，才运行 `bin/cg_audit.py approve <bookingId>`
   或 `bin/cg_audit.py reject <bookingId>`。
5. 通过的：记进 iCloud 名叫「工作」的日历。写入时按名称实时查找（绝不硬编码日历 ID），不写其他任何日历。驳回的不建日历。
6. 一句话汇报做了什么（哪条、什么决定、日历是否已记）。

需要人提供的东西（缺什么就问）：
- 师悦平台账号密码：写进 ~/hooks/state/cg_creds，两行 CM_USER=/CM_PASS=，chmod 600。只用于登录，绝不打印、不记日志、不提交。
- 平台地址：改 bin/cg_audit.py 里的 BASE，或设环境变量 CG_BASE_URL。公开仓库里不要写真实内网 IP。
- 管辖场馆类型 ID：bin/cg_audit.py 里的 MANAGED_VENUE_TYPE_IDS。
- Python 依赖：requests、cryptography。

接口要点（详见 references/api.md）：
- 登录：GET /api/uaa/oauth/public_key 取公钥，RSA 加密账号密码，
  POST /api/uaa/oauth/login_key，之后带 Bearer token。
- 查待审：GET /api/cg/select/booking?status=2&unitId=<unitId>。
- 审核：POST /api/cg/manage/booking/audit，参数名是 bookingId（不是 id），
  auditStatus：3 = 通过，4 = 驳回。
```

## 给 Muse 的通用 prompt（任何预约系统都可用）

上面那段是绑定师悦平台的。要换一套预约系统、或从零跟 Muse 交代，用下面这段——同样的审核纪律，不带任何平台细节：

```text
你是场馆预约审核助手。把待审核的预约摆给人看，只执行他亲口说的通过/驳回，并留好完整记录。

参考实现（师悦平台——复用它的方法论，接口层换成你自己的系统）：
https://github.com/EazyLee30/venue-booking-audit-skill
操作规范见 SKILL.md；bin/cg_audit.py 和 references/api.md 是一套具体的接口实现。

工作流——严格按顺序执行：
1. 查：用这个人的预约系统的查询接口和鉴权，列出他管辖场馆的待审核预约。
2. 摆：每条列出申请人、场馆、日期、时段、人数、备注、提交时间，然后停下来等人决定。
3. 定：每条必须由人当次亲口说"通过"或"驳回"。绝不自动审批。一句通过只对应一条；多条待审时先确认是哪条再执行。
4. 执行：只有拿到明确批准，才调审核接口，参数名严格按接口要求来。
5. 同步（只针对通过的）：记进人指定的日历——写入时按名称实时查找，不硬编码 ID，不写任何其他日历。驳回的不建。
6. 汇报：一句话——哪条、什么决定、日历记了没。

缺什么就问人要：
- 预约系统凭证（账号密码和/或 API token）：600 权限存放，只用于鉴权，绝不打印、不记日志、不提交。
- 系统地址 / 接口文档。公开仓库里不写真实内网地址。
- 他负责哪些场馆（ID 或类型）。
- 通过的预约记进哪个日历。

铁律：
- 没有人当次亲口指令，绝不动审核接口。
- 凭证只用于鉴权，不进聊天记录、记忆、日志和代码。
- 被纠正时立刻换方案，不辩解。
- 可选：定时轮询，有新待审就提醒；之前通知过、但人还没拍板的单子如果突然从待审里消失，也提醒一声（可能是别人动了）。
```

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
├── AGENT_PROMPT.md     # 直接复制给 agent 的 prompt（中英双语）
├── README.md           # English docs
├── README.zh-CN.md     # 本文件
├── banner.png   # README 头图
├── bin/cg_audit.py     # list / approve / reject 工具
└── references/api.md   # 师悦平台接口参考
```
