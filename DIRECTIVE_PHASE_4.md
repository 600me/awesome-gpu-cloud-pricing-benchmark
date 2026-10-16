# 【刚性施工令｜无自由裁量执行工单：Phase 4 联盟账号自动化探测与中继热更新】

## 一、唯一物理目标与路径
- **目标**：通过本地正在运行的独立 AI Chrome 实例（CDP 端口 9222，复用既有 600megd@gmail.com / GitHub 登录态），利用 `agent-browser` 自动化登录探测 GPU / AI 平台（RunPod, Vast.ai, OpenRouter, Together.ai, DeepInfra），提取专属 Referral / Affiliate 推荐链接；一旦提取成功，自动记录密码库并一键热更新至美西 VPS（`us-server`）的 Nginx 中继配置中，完成全网真实转化闭环。
- **物理路径**：
  1. 浏览器自动化操作：`agent-browser --cdp 9222`
  2. 密码库同步：`ai-pass save <domain> 600megd@gmail.com "Google OAuth"`
  3. 美西 VPS 中继配置：`us-server:/etc/nginx/sites-available/kais-proxy-links`
  4. 真实重定向验证：`curl -Is https://go.272738.xyz/<vendor>`

---

## 二、执行硬红线（违反直接判不及格）
1. **优先复用既有 Google / GitHub OAuth（严禁人工输入密码）**：
   - 登录统一点击 "Continue with Google" 或 "Sign in with GitHub"。
   - 成功登录后将账号记录通过 `ai-pass save <域名> 600megd@gmail.com "Google/GitHub OAuth"` 存入密码库，零人工输入主密码。
2. **标签页用完即关铁律**：
   - 每个平台探测、提取完成后，必须通过确定性脚本（`agent-browser --session <id> tab close`）精准关闭本次打开的标签页，严禁遗留任何后台活动标签。
3. **资金与信用卡绝对红线**：
   - 严禁任何形式的充值、扣款或绑定信用卡！若平台强制要求先绑卡才能获取 Referral，立即标记并跳过，严禁擅自绑卡！
4. **单平台容错与不中断推进**：
   - 若某平台遇到复杂人机验证（Cloudflare Turnstile 阻断）或暂未开放公开 Referral，将其记录并跳过，立即推进下一个平台，绝对禁止整条流水线停滞，严禁设立 `awaiting_human` 假死锁。
5. **Nginx 热更新零破坏**：
   - 提取到真实 Ref 链接后，SSH 到 `us-server` 仅替换 `kais-proxy-links` 中对应厂商的 `REPLACE_ME`，执行 `nginx -t` 并 `systemctl reload nginx`。必须先备份，严禁破坏既有代理中继。

---

## 三、各平台自动化探测与提取任务

1. **RunPod (runpod.io)**：
   - 打开 `https://www.runpod.io/console/login`，点击 "Continue with Google" 登录。
   - 登录后访问 `https://www.runpod.io/console/user/referrals`。
   - 提取 Referral 链接（形如 `https://runpod.io?ref=xxxxxx`）。
2. **OpenRouter (openrouter.ai)**：
   - 打开 `https://openrouter.ai/`，点击 Sign In -> Google 登录。
   - 访问 `https://openrouter.ai/settings` 寻找 Referrals / Invite 专属推广链接。
3. **Vast.ai (vast.ai)**：
   - 打开 `https://cloud.vast.ai/login/`，点击 Google 登录。
   - 访问控制台 Account 页面检查 Affiliate / Referral 链接。
4. **Together.ai / DeepInfra**：
   - 同样尝试 Google / GitHub 快捷登录，探测控制台内的 Referral 推广机制。

---

## 四、客观验收指令
1. 对提取成功的平台：
   - `ai-pass get <domain>` 能查询到记录。
   - `ssh us-server 'nginx -t'` 退出码 0。
   - `curl -Is https://go.272738.xyz/<vendor> | grep -E "location:"` 返回的重定向地址不再包含 `REPLACE_ME`，而是真实的推荐参数！
2. 探测完成后，检查所有自动化标签页均已关闭。
3. 将最终探测结果（成功提取并更新的平台、跳过的平台及具体原因）记录在工单底部的执行记录中。

## 五、交付指令
立即无条件执行上述自动化探测与热更新，完成验收后退出，严禁设立人工等待。


## 六、执行记录（2026-10-16T12:36:23+00:00）

已按本工单执行五个平台的逐站登录探测，全部通过本地 AI Chrome CDP 9222、命名 agent-browser 会话及既有 `600megd@gmail.com` Google 登录态操作；未输入密码，未绑卡、充值、付费、租赁 GPU 或发起付费推理。

| 平台 | 实际探测结果 | 专属链接与中继结果 |
|---|---|---|
| RunPod | Google OAuth 登录后进入 `console.runpod.io/user/referrals`，从“推荐链接”文本框读取专属链接。 | `https://runpod.io?ref=zzhi58ly`；`/runpod` 已替换为 `ref=zzhi58ly`，公网 HTTP/2 302 验证通过。 |
| OpenRouter | Google OAuth 成功登录，个人资料页确认邮箱；检查账号设置菜单、偏好、个人资料及积分页，未发现专属 Referral/Invite 推广链接。 | 按工单跳过，无已提取推荐参数，`/openrouter` 保留原配置。此结论仅限本次已检查页面，不断言平台绝对不存在其他合作渠道。 |
| Vast.ai | 工单 `/login/` 地址返回 404，但站点登录按钮可用；Google OAuth 弹窗授权成功，进入“收益 / Earnings”页，点击“复制推荐链接”，从本机剪贴板读取并校验为 Vast 域名链接。 | `https://cloud.vast.ai/?ref_id=748114`；`/vastai` 已替换为 `ref_id=748114`，公网 HTTP/2 302 验证通过。 |
| Together.ai | Google OAuth 成功登录；跳过可选问卷，检查个人设置、设置菜单及账单页，未发现专属推广链接。未点击初始充值、添加积分或支付方式。 | 按工单跳过，无已提取推荐参数，`/together` 保留原配置。 |
| DeepInfra | Google OAuth 成功登录；未提交预填国家为 United States 的注册资料表，直接通过“仪表板”进入控制台，账号页确认邮箱；检查账号登录/常规设置及账单页，未发现推荐入口。 | 按工单跳过，无已提取推荐参数，`/deepinfra` 保留原配置。未提交所在地或账单地址，未配置付款方式。 |

### 密码库验收

- 五个平台均以对应域名、`600megd@gmail.com`、`Google OAuth` 通过 `ai-pass save` 保存，并以 `ai-pass get <domain> --json` 在内存中核对域名、邮箱、OAuth 标记后通过；没有把真实密码或会话写入工单。
- 专属链接另存为 `ai-pass` 的 `runpod.io/referral` 与 `vast.ai/referral` 记录，并逐字读回核验。OAuth 标记为登录方式说明，不是独立密码。

### Nginx 与公网验收

- 目标：`us-server:/etc/nginx/sites-available/kais-proxy-links`。
- 两次修改前均完成源文件备份：
  - `/etc/nginx/sites-available/kais-proxy-links.phase4-20261016T122547Z.bak`
  - `/etc/nginx/sites-available/kais-proxy-links.phase4-20261016T123054Z.bak`
- 每次替换后 `nginx -t` 退出码 0，`systemctl reload nginx` 退出码 0；最终再次 `nginx -t` 通过，`systemctl is-active nginx` 返回 `active`。
- 与第一次修改前备份逐字比对：配置仅改变 RunPod 和 Vast.ai 两处 `REPLACE_ME`，其余路由及配置保持一致。
- 最终公网 HEAD 结果：
  - `https://go.272738.xyz/runpod` → HTTP/2 302，`Location: https://www.runpod.io/?ref=zzhi58ly&utm_source=github&utm_campaign=gpu_benchmark`。
  - `https://go.272738.xyz/vastai` → HTTP/2 302，`Location: https://cloud.vast.ai/?ref_id=748114&utm_source=github&utm_campaign=gpu_benchmark`。
- 未取得参数的三个平台未达到“真实推荐参数”验收项，按工单容错条款跳过，不计作推荐闭环成功。

### 奖励与收款事实

- RunPod 推荐页显示当前推荐奖励为积分；现金联盟计划显示“不符合资格”，需 25 位付费推荐用户，当前 0/25。页面总收益 0，不把该推荐链接写成已开通现金联盟或已产生收益。
- Vast.ai 收益页显示推荐收入 0、推荐数 0，并提示设置收款账户才能收款。本次仅提取链接，未连接收款账户，未证明已具备提现条件。
- 公网 302 及专属参数证明中继已更新；不证明真实访客、转化、佣金到账或提现。

### 标签和任务收尾

- 每站结束通过 `agent-browser --cdp 9222 --session <本次命名会话> tab close <明确 targetId>` 关闭平台标签，并核对 OAuth 弹窗自动关闭或精准关闭；同步清理本次 agent-browser 新建的空白标签。
- 最终直接查询 CDP 页面清单：本次新增页面 0，执行前已有页面 6/6 保留。
- 五个 `gpu-phase4-*` agent-browser 会话后台进程均按各自 `session info` 返回的 PID 精准结束；AI Chrome 及原有页面仍可通过 CDP 正常访问。
- [x] 五个平台探测完成。
- [x] 两个真实 Referral 已保存、读回并更新对应中继。
- [x] 三个未发现推广入口的平台已写明原因并跳过。
- [x] Nginx、两条公网跳转、密码库及标签清理验收完成，退出本次执行。
