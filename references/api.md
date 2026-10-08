# 未来校园场馆预约 API 参考

Base: `http://<your-shiyue-host>:<port>`（你学校的师悦平台地址）

## 登录
1. `GET /api/uaa/oauth/public_key` → `data` 为 PEM 公钥（DER base64，可能含换行）。
2. 用公钥 RSA/PKCS1v15 加密 `username`、`password`，base64 后作为 `username`/`password` 字段；
   另传 `signature = "SYSN_" + 毫秒时间戳`。
3. `POST /api/uaa/oauth/login_key`（form-data）。成功返回 `code: "ok"` 且
   `data.authenticated == true`；后续请求带 `Authorization: Bearer <accessToken>`。
4. `data.unitId` 用于按单位查预约。

请求头建议：`User-Agent: Mozilla/5.0`，`Origin`/`Referer` 设为 BASE。

## 查待审核
`GET /api/cg/select/booking`
params: `start=1`, `size=50`, `unitId=<unitId>`, `status=2`
返回 `data.list`；逐条确认 `status == 2`（字符串 "2" 也算）。

相关字段：
- `id` → 预约 ID（审核用）
- `venueName` / `venueTypeName` → 场馆
- `venueTypeId` → 场馆类型；示例：`13` 实验室，`15` 声乐教室，`17` 大礼堂
- `useUserName`（无则 `creatorName`）→ 申请人
- `bookingEnd[:10]` → 日期；`sectionName` → 时段（如 `15:30-16:40`）
- `persons` → 使用人数；`useRemark`/`remark` → 备注；`createdDate` → 提交时间

## 审核
`POST /api/cg/manage/booking/audit`（form-data）：
- `bookingId`: 预约 ID（注意不是 `id`）
- `auditStatus`: `3` 通过，`4` 驳回

成功返回 `{"status":200,"code":"ok","data":"success"}`。

## 已验证的坑
- 审核接口参数名是 `bookingId`；传 `id` 会报 `missing_servlet_request_parameter`。
- 登录密码是 RSA 加密传输；`cryptography` 包缺失会导致登录代码 import 失败。
  VM 重装/重启可能清空系统 python 的包，监控脚本应自检并重装（见主仓库 hook 写法）。
- 用户改密码后所有登录失效：只提醒重新提供凭证，不自行处理。
